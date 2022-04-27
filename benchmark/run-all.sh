start=$(date)
bash run-benchmark.sh queries/bgps/
end1=$(date)
bash run-benchmark.sh queries/optionals/
end2=$(date)
bash run-benchmark.sh queries/existence_check/
end3=$(date)
bash run-benchmark.sh queries/empty/
end4=$(date)
bash run-benchmark.sh queries/modified_bgps/
end5=$(date)
bash run-benchmark.sh queries/specialized/
end6=$(date)

echo
echo "STARTED AT:"
echo $start
echo
echo "BGPS DONE AT:"
echo $end1
echo
echo "OPTIONALS AT:"
echo $end2
echo
echo "EXISTENCE CHECK AT:"
echo $end3
echo
echo "EMPTY AT:"
echo $end4
echo
echo "MODIFIED BGPS AT:"
echo $end5
echo
echo "SPECIALIZED AT:"
echo $end6
