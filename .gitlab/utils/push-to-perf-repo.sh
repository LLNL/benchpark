#!/bin/bash
set -euo pipefail

summary_dir="${CI_PROJECT_DIR}/artifact-test-summary"
perf_repo_url="${BENCHPARK_PERF_REPO_URL:-https://github.com/llnl/benchpark-performance.git}"
perf_repo_dir="$(mktemp -d)"
askpass_script="${perf_repo_dir}.askpass"
host_dirs=(dane tioga matrix tuolumne)

cleanup() {
    rm -rf "${perf_repo_dir}"
    rm -f "${askpass_script}"
}
trap cleanup EXIT

if [[ -z "${BENCHPARK_PERF_DEPLOY_TOKEN:-}" ]]; then
    echo "BENCHPARK_PERF_DEPLOY_TOKEN is required to push benchpark-performance updates." >&2
    exit 1
fi

if [[ ! -d "${summary_dir}" ]]; then
    echo "Missing nightly metadata directory: ${summary_dir}" >&2
    exit 1
fi

cat > "${askpass_script}" <<'EOF'
#!/bin/bash
case "$1" in
    *Username*) printf '%s\n' "x-access-token" ;;
    *Password*) printf '%s\n' "${BENCHPARK_PERF_DEPLOY_TOKEN}" ;;
    *) exit 1 ;;
esac
EOF
chmod 700 "${askpass_script}"

GIT_ASKPASS="${askpass_script}" GIT_TERMINAL_PROMPT=0 \
    git clone "${perf_repo_url}" "${perf_repo_dir}"

copied=0
for host in "${host_dirs[@]}"; do
    if [[ -d "${summary_dir}/${host}" ]]; then
        mkdir -p "${perf_repo_dir}/${host}"
        find "${summary_dir}/${host}" -maxdepth 1 -type f -name '*.json' -exec cp {} "${perf_repo_dir}/${host}/" \;
        copied=1
    fi
done

if [[ "${copied}" -eq 0 ]]; then
    echo "No host metadata JSON files found in ${summary_dir}; nothing to deploy."
    exit 0
fi

cd "${perf_repo_dir}"

if [[ -z "$(git status --porcelain -- "${host_dirs[@]}")" ]]; then
    echo "No benchpark-performance metadata changes to commit."
    exit 0
fi

git config user.name "${GITLAB_USER_NAME:-benchpark-ci}"
git config user.email "${GITLAB_USER_EMAIL:-benchpark-ci@llnl.gov}"

git add "${host_dirs[@]}"
git commit -m "Update nightly performance metadata from ${CI_PIPELINE_ID:-unknown}"
GIT_ASKPASS="${askpass_script}" GIT_TERMINAL_PROMPT=0 \
    git push origin HEAD
