NB_CHECKS=0
NB_SKIPPED=0
NB_SUCCESS=0
NB_FAILURE=0
for check_input in checks/*.input; do
  NB_CHECKS=$(( NB_CHECKS + 1 ))
  echo
  echo "----------------------------------------------------------------"
  echo "Checking input file '$check_input'"
  # replace 'input' at the end of `check_input` with 'output'
  check_output="${check_input/%input/output}"
  if ! [[ -f "$check_output" ]]; then
    NB_SKIPPED=$(( NB_SKIPPED + 1 ))
    echo "Corresponding check output ('$check_output') does not exist, skipping"
    continue
  fi
  echo "--- Running challenge code with the input ---"
  output=$(python main.py < "$check_input")
  echo "--- START OF OUTPUT"
  echo "$output" # note: here we add a newline, even if the output originally didn't have one
  echo "--- END OF OUTPUT"

  if [[ "$output" == "$(cat "$check_output")" ]]; then
    NB_SUCCESS=$(( NB_SUCCESS + 1 ))
    echo
    echo "SUCCESS :) output of the code matches expected output!"
    echo
  else
    NB_FAILURE=$(( NB_FAILURE + 1 ))
    echo
    echo "FAILURE :( output of the code does not match the expected output...."
    echo
    echo "--- START OF EXPECTED OUTPUT"
    cat "$check_output"
    echo "--- END OF EXPECTED OUTPUT"
    echo
  fi
done

echo "=--=--=--=--=--=--=--=--=--=--="
echo "Nb checks: $NB_CHECKS"
echo "Nb success: $NB_SUCCESS"
echo "Nb failure: $NB_FAILURE"
echo "Nb skipped: $NB_SKIPPED"
echo "=--=--=--=--=--=--=--=--=--=--="
