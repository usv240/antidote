#!/usr/bin/env bash
# Public guideline and registry documents for Antidote. Indexed locally; licence per data/manifest.yaml.
set -uo pipefail
UA="Mozilla/5.0 (Antidote corpus fetch; non-commercial)"
get () { [ -s "$2" ] && return; curl -sL -A "$UA" --retry 2 -o "$2" "$1" || echo "FAILED $1"; sleep 1; }
get "https://iris.who.int/bitstream/handle/10665/332193/9789240005662-eng.pdf" data/corpus/guidelines/who_pesticide_hazard_classification_2019.pdf
get "https://nhsrcindia.org/sites/default/files/2022-11/Emergency%20Care%20for%20MO-%20General%20Approach%20to%20Poison%20Management.pdf" data/corpus/guidelines/nhsrc_emergency_care_mo_poison_management.pdf
get "https://www.ijccm.org/doi/pdf/10.5005/jp-journals-10071-24697" data/corpus/guidelines/isccm_2024_acute_poisoning_position_statement.pdf
get "https://nhsrcindia.org/sites/default/files/2021-05/The%20Insecticides%20rules%201971.pdf" data/corpus/registries/insecticides_rules_1971.pdf
get "https://qi.nhsrcindia.org/sites/default/files/medico_legal.pdf" data/corpus/guidelines/nhsrc_medico_legal_guideline.pdf
get "https://ppqs.gov.in/sites/default/files/major_uses_of_pesticides_insecticides_as_on_31.03.2024.pdf" data/corpus/registries/cibrc_major_uses_insecticides_2024.pdf
for f in data/corpus/*/*.pdf; do printf "%s  %s bytes  %s\n" "$f" "$(stat -c %s "$f")" "$(head -c 4 "$f")"; done
