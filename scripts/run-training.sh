#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "${SCRIPT_DIR}/.." && pwd)

PIPELINE_ARG=""
DATASET_ARG=""
OUTPUT_ARG=""
CHECK=false

while [[ $# -gt 0 ]]; do
	case "$1" in
	--dataset)
		shift
		DATASET_ARG="${1-}"
		;;
	--output)
		shift
		OUTPUT_ARG="${1-}"
		;;
	--check)
		CHECK=true
		;;
	-*)
		echo "[run-training] Unknown argument: $1" >&2
		exit 2
		;;
	*)
		if [[ -z ${PIPELINE_ARG} ]]; then
			PIPELINE_ARG="$1"
		else
			echo "[run-training] Unexpected positional argument '$1'" >&2
			exit 2
		fi
		;;
	esac
	shift
done

PYTHON_SCRIPT="${SCRIPT_DIR}/run-training.py"
CMD=("python3" "${PYTHON_SCRIPT}")
if [[ -n ${PIPELINE_ARG} ]]; then
	CMD+=("${PIPELINE_ARG}")
fi
if [[ -n ${DATASET_ARG} ]]; then
	CMD+=("--dataset" "${DATASET_ARG}")
fi
if [[ -n ${OUTPUT_ARG} ]]; then
	CMD+=("--output" "${OUTPUT_ARG}")
fi
if [[ ${CHECK} == "true" ]]; then
	CMD+=("--check")
fi

exec "${CMD[@]}"
