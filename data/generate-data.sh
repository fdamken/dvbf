#!/usr/bin/env bash

set -o errexit
set -o nounset

export PYTHONPATH=..

parent_out_dir="sequences"
tmp_parent_out_dir="tmp_$parent_out_dir"

if [[ -e "$parent_out_dir" ]]; then
    echo "E: Output directory '$parent_out_dir' exists. Cannot continue."
    exit 126
fi

rm -rf "$tmp_parent_out_dir"
mkdir "$tmp_parent_out_dir"

max_seed=10000
max_processes="$(grep -c '^processor' /proc/cpuinfo)"
n=0
for seed in $(seq 1 $max_seed); do
    if [[ "$n" == "$max_processes" ]]; then
        wait
        n=0
    fi

    echo "Generating pendulum sequences using seed $seed/$max_seed (process $((n + 1))/$max_processes)."
    (
        python pendulum.py "$tmp_parent_out_dir/$seed" -s -c "$seed"
        echo "Generation for seed $seed/$max_seed finished."
    ) &

    n=$((n + 1))
done

mv "$tmp_parent_out_dir" "$parent_out_dir"
