echo "Transfering..."

for folder in queries/*[^.txt]; do
    for result_folder in $folder/output/*; do
        result_folder_name=${result_folder:8:-9}
        mv $result_folder/* ../results/$result_folder_name
    done
done

echo "Done"
