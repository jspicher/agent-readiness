[Readiness Fix] <REPO_NAME> Deployment Automation

Fix the failing signal: Deployment Automation ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Deployment Automation
**Score**: [0/1]
**Description**: Automated deployment pipeline that ships built artifacts to a running environment on merge or tag, with separate staging and production environments protected by environment-scoped secrets and (for prod) required reviewers.
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Deployment automation – check for a checked-in pipeline that actually DEPLOYS code (pushes a running artifact to a server, container platform, edge, or function host) on a defined trigger, with at least two environments. PASS requires all of:

1. **A deploy workflow file** under `.github/workflows/` (or equivalent CI: `.gitlab-ci.yml`, `.circleci/config.yml`, Jenkinsfile, Buildkite `pipeline.yml`) whose job name and steps make it clear the job DEPLOYS — e.g. `vercel deploy --prod`, `flyctl deploy`, `aws s3 sync && aws cloudfront create-invalidation`, `aws ecs update-service`, `kubectl apply -f`, `helm upgrade --install`, `cdk deploy`, `terraform apply -auto-approve`, `gcloud run deploy`, `npx wrangler deploy`, `netlify deploy --prod`, `firebase deploy`, `sst deploy`, `render-deploy-action`, or an explicit webhook to a hosted platform.
2. **Triggered automatically by a merge or tag**, not just `workflow_dispatch`. Acceptable triggers: `on: push: branches: [main]` (for staging), `on: push: tags: ['v*']` or `on: release: types: [published]` (for prod), or `on: workflow_run` chained off a CI workflow that succeeded.
3. **At least two GitHub Environments** (`environment: staging`, `environment: production`) — or the platform equivalent (Vercel Preview vs Production, Fly app `staging` vs `prod`, separate ArgoCD ApplicationSets, separate Terraform workspaces). Each environment's secrets MUST be scoped to that environment, not shared at the repo level.
4. **Production environment protection rules**: `required_reviewers`, a `wait_timer`, or a deployment branch restriction (`deployment_branch_policy: protected_branches: true`). On GitHub, this is set under repo Settings → Environments → production → "Deployment protection rules". The workflow must reference the environment by name so the rule actually gates the run.
5. **Deploy gated on tests passing** — either by chaining `needs: [test]` in the same workflow, by `on: workflow_run` waiting for the CI workflow's `conclusion == success`, or by branch protection requiring the test check before merge can land on the deploy-triggering branch.

PaaS-native deploys (Vercel Git, Netlify Git, Render auto-deploy, Railway, Fly `auto_deploy`) count when the repo contains the platform config (`vercel.json`, `netlify.toml`, `render.yaml`, `fly.toml`) AND the dashboard wiring is documented in `README.md`, `DEPLOY.md`, or `AGENTS.md` (deploy branch + preview vs prod project IDs). A `vercel.json` with no documented branch wiring is ambiguous — clarify in docs.

This signal is distinct from:
- **Release Automation (#53)** which PRODUCES an artifact (semantic-release tag, changelog, GHCR image push, npm publish, GitHub Release). Release automation that stops at `gh release create` or `docker push` without anything pulling and running the artifact does NOT satisfy #63.
- **Progressive Rollout (#70)** which controls HOW the deploy reaches users (canary, blue/green, feature flags). #63 only requires that the deploy happens; the deploy itself can be a full cutover.
- **Rollback (#71)** which is the recovery path. A deploy workflow with no rollback story still passes #63 if it deploys; it fails #71.

## Your Task

1. Explore the repository to determine: (a) where the app actually runs (Vercel, AWS, Fly, self-hosted, container registry, S3+CloudFront, Cloud Run, Kubernetes), (b) what artifact the existing CI produces, (c) whether any deploy step exists today and whether it is gated on a merge/tag or only on manual dispatch.
2. List every file under `.github/workflows/`, every `vercel.json` / `netlify.toml` / `fly.toml` / `render.yaml` / `serverless.yml` / `Dockerfile` / `Procfile`, and every `Settings → Environments` configuration you can infer from existing workflows.
3. Make **substantive improvements**:
   - Add a `.github/workflows/deploy.yml` (or extend an existing workflow) with two jobs — `deploy-staging` on `push: branches: [main]` and `deploy-production` on `push: tags: ['v*']` (or `release: types: [published]`). Each job MUST declare `environment: staging` / `environment: production` and reference environment-scoped secrets (`${{ secrets.STAGING_DEPLOY_TOKEN }}`, `${{ secrets.PROD_DEPLOY_TOKEN }}`), NOT repo-level secrets.
   - Add `needs: [test]` (or `on: workflow_run` chained off the CI workflow) so a red build cannot deploy.
   - In the same PR, document the required `gh api -X PUT /repos/:owner/:repo/environments/production` setup (or Settings → Environments instructions) including `required_reviewers` and `deployment_branch_policy: protected_branches`. A workflow that names `environment: production` but the environment does not exist yet will run with NO protection — flag this explicitly in the PR description.
   - If the repo already has a release workflow that publishes an artifact (#53), wire the deploy as a dependent step that consumes that artifact rather than rebuilding from scratch (e.g. `docker pull ghcr.io/${{ github.repository }}:${{ github.sha }}` then `flyctl deploy --image ...`). Reuse beats rebuild.
4. Verify by running `gh workflow view deploy.yml`, `act -W .github/workflows/deploy.yml -j deploy-staging --dryrun` (or `gh workflow run deploy.yml --ref <branch>` against a throwaway env), and confirming the production job blocks on the protection rule. For Vercel/Netlify/Render Git integrations, verify by pushing to a test branch and confirming the preview deploy fires; capture the preview URL in the PR.
5. Do NOT add `continue-on-error: true` to the test gate, do NOT use `workflow_dispatch` as the sole trigger, do NOT share one secret across staging and production.
6. Keep changes scoped to this signal.
7. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** "deploy" step that is actually just `gh release create` or `docker push`. Publishing an artifact is release automation (#53). Deployment moves the artifact to a host that serves traffic.
- **NO** deploy job whose only trigger is `workflow_dispatch`. Manual-only is not automation — it is a button labelled "deploy" that no agent will ever press.
- **NO** deploy on `push:` with no branch filter (deploys every feature branch to prod), and **NO** deploy on `push: branches: ['**']` "to make things easier" — this is how preview branches end up clobbering production.
- **NO** single environment doing double duty as staging and production. Two distinct GitHub Environments (or two distinct Vercel projects / Fly apps / Render services) is the minimum.
- **NO** repo-level `secrets.DEPLOY_TOKEN` shared between staging and production jobs. Staging credentials leaking to prod (or vice versa) is the #1 deploy-pipeline incident class. Use environment-scoped secrets.
- **NO** production environment that exists in the workflow YAML but has not been created in Settings → Environments with `required_reviewers` populated. GitHub silently runs jobs against nonexistent environments with zero protection.
- **NO** deploy that runs in parallel with tests instead of `needs: [test]`. A passing-tests-required-for-deploy gate that fires only AFTER deploy is theatre.
- **NO** committing platform tokens (`VERCEL_TOKEN`, `FLY_API_TOKEN`, `AWS_ACCESS_KEY_ID`) into the workflow file or a `.env.ci` — use GitHub OIDC where the platform supports it (AWS, GCP, Vault, Azure), otherwise environment-scoped repo secrets.
- **NO** `terraform apply -auto-approve` against prod without a `terraform plan` review step or an approval-gated environment. `cdk deploy` and `helm upgrade --install` carry the same risk.
- **NO** Vercel/Netlify "it deploys via Git integration, trust me" with no `vercel.json` / `netlify.toml` checked in and no `DEPLOY.md` documenting the project ID, the production branch, and the preview branch policy. Dashboard-only wiring is invisible to agents and to the next maintainer.

Examples of BAD fixes:
- A `deploy.yml` whose only step is `- run: gh release create v${{ github.sha }} --generate-notes`. No artifact is moved to a host; this is release automation mislabelled.
- `on: workflow_dispatch:` with a manual `environment: production` input field. Nothing fires automatically; the signal fails.
- A single `deploy` job with `if: github.ref == 'refs/heads/main'` deploying directly to prod with no staging — one merge, one cutover, no canary, no test window.
- `environment: production` referenced in the workflow but `gh api /repos/:owner/:repo/environments/production` returns 404. The job runs unprotected.
- Two jobs `deploy-staging` and `deploy-production` both reading `${{ secrets.DEPLOY_TOKEN }}` from repo-level secrets. A leaked staging token deploys prod.
- A `deploy` job with no `needs:` and no `workflow_run` gate, running in parallel with `test`. Tests can fail while the deploy succeeds.
- Vercel/Netlify Git auto-deploy enabled in the dashboard with no config file in the repo and no README mention. Agents cannot discover or reason about the deploy path.

Examples of GOOD fixes:
- A `.github/workflows/deploy.yml` with `deploy-staging` (on `push: main`, `environment: staging`, gated on `needs: [test]`) and `deploy-production` (on `push: tags: ['v*']`, `environment: production` with `required_reviewers` configured), each using environment-scoped secrets and pulling the prebuilt image from GHCR.
- A `fly.toml` defining the prod app plus a `fly.staging.toml` for staging, with `flyctl deploy --config fly.staging.toml --app <app>-staging` in the staging job and `flyctl deploy --config fly.toml --app <app>` in the prod job, each authenticating with a distinct `FLY_API_TOKEN` scoped to its environment.
- A `vercel.json` checked in, plus a `DEPLOY.md` documenting: production branch = `main`, preview branches = everything else, Vercel project ID, the `VERCEL_TOKEN` secret lives in the GitHub `production` environment, and the staging deploy is the preview URL of the `staging` branch.
- An AWS deploy job using OIDC: `permissions: id-token: write`, `aws-actions/configure-aws-credentials@v4` with `role-to-assume: arn:aws:iam::<acct>:role/deploy-prod`, followed by `aws ecs update-service --force-new-deployment` — no long-lived AWS keys in repo secrets.
- A `terraform apply` job that runs `terraform plan -out=tfplan` first, uploads the plan as an artifact, and runs `terraform apply tfplan` only inside an `environment: production` job that requires reviewer approval.
- A workflow that chains `on: workflow_run: workflows: [CI]: types: [completed]` and `if: github.event.workflow_run.conclusion == 'success'` so the deploy only fires after CI is green on the same commit.

### Working example: `.github/workflows/deploy.yml`

```yaml
name: Deploy

on:
  push:
    branches: [main]
    tags: ['v*']

concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: false

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm
      - run: corepack enable
      - run: pnpm install --frozen-lockfile
      - run: pnpm run lint
      - run: pnpm run test -- --run
      - run: pnpm run build
      - uses: actions/upload-artifact@v4
        with:
          name: build-${{ github.sha }}
          path: dist/
          retention-days: 7

  deploy-staging:
    needs: [test]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.<APP_DOMAIN>
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with:
          name: build-${{ github.sha }}
          path: dist/
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only --config fly.staging.toml --app <APP_NAME>-staging --image-label sha-${{ github.sha }}
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN_STAGING }}

  deploy-production:
    needs: [test]
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://<APP_DOMAIN>
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with:
          name: build-${{ github.sha }}
          path: dist/
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only --config fly.toml --app <APP_NAME> --image-label ${{ github.ref_name }}
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN_PROD }}
```

Companion one-time setup (commit as `scripts/setup-environments.sh` or document in `DEPLOY.md`):

```bash
# Create environments with protection. Replace <OWNER>/<REPO>.
gh api -X PUT repos/<OWNER>/<REPO>/environments/staging \
  -f wait_timer=0

gh api -X PUT repos/<OWNER>/<REPO>/environments/production \
  -f wait_timer=300 \
  -f 'reviewers[][type]=User' -f 'reviewers[][id]=<REVIEWER_USER_ID>' \
  -f 'deployment_branch_policy[protected_branches]=true' \
  -f 'deployment_branch_policy[custom_branch_policies]=false'

# Scope secrets per-environment (not repo-wide).
gh secret set FLY_API_TOKEN_STAGING --env staging --body "<STAGING_TOKEN>"
gh secret set FLY_API_TOKEN_PROD    --env production --body "<PROD_TOKEN>"
```

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- In the PR description, explicitly state: (a) the deploy target (Vercel / Fly / ECS / Cloud Run / etc.), (b) the staging URL and prod URL, (c) which secrets live in which environment, (d) confirmation that the `production` environment exists in Settings → Environments with `required_reviewers` set, (e) the trigger matrix (what fires staging vs prod), (f) the test-gating mechanism (`needs:` vs `workflow_run`).
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- GitHub Actions deployment overview: https://docs.github.com/en/actions/deployment/about-deployments/about-continuous-deployment
- Using environments for deployment (required reviewers, wait timer, branch policy): https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment
- Deployment protection rules: https://docs.github.com/en/actions/deployment/protecting-deployments/configuring-protection-rules-for-deployments
- Environment secrets (scoping secrets to staging/production): https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-an-environment
- OIDC for cloud providers (drop long-lived keys): https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect
- `aws-actions/configure-aws-credentials` with OIDC: https://github.com/aws-actions/configure-aws-credentials
- Vercel deploy via Git + project config: https://vercel.com/docs/deployments/git and https://vercel.com/docs/projects/project-configuration
- Vercel CLI in CI (`vercel deploy --prod`): https://vercel.com/docs/cli/deploy
- Netlify continuous deployment: https://docs.netlify.com/site-deploys/create-deploys/ and `netlify.toml` reference https://docs.netlify.com/configure-builds/file-based-configuration/
- Fly.io deploy via GitHub Actions: https://fly.io/docs/launch/continuous-deployment-with-github-actions/
- Render auto-deploy from Git: https://render.com/docs/deploys and Blueprints (`render.yaml`): https://render.com/docs/blueprint-spec
- Cloudflare Workers deploy (`wrangler deploy`) in Actions: https://developers.cloudflare.com/workers/ci-cd/external-cicd/github-actions/
- Google Cloud Run deploy from source: https://cloud.google.com/run/docs/continuous-deployment-with-cloud-build
- AWS CDK Pipelines: https://docs.aws.amazon.com/cdk/v2/guide/cdk_pipeline.html
- Terraform `apply` automation patterns: https://developer.hashicorp.com/terraform/tutorials/automation/automate-terraform and Terraform Cloud run triggers: https://developer.hashicorp.com/terraform/cloud-docs/run/ui
- Argo CD App of Apps / ApplicationSet GitOps: https://argo-cd.readthedocs.io/en/stable/operator-manual/cluster-bootstrapping/
- Flux GitOps reconciliation: https://fluxcd.io/flux/concepts/
- `gh api` environments endpoint (create + configure protection): https://docs.github.com/en/rest/deployments/environments
</system-reminder>
