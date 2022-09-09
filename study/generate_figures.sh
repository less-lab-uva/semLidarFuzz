printf "Setting up Docker container\n"
docker-compose up --build -d
printf "Checking if study data has been downloaded\n"
docker-compose exec figs bash -c "mkdir /root/study_data 2>/dev/null"
docker-compose exec figs bash -c "test -f \"/root/study_data/.keep\" && printf \"Files already downloaded\n\" || ( python3 -c 'import gdown; gdown.download(id=\"1Vb7CK6ug6btSEJaue7jXqiM8pP_iT6BE\", output=\"/root/study_data.tar.xz\", quiet=False)' && printf \"Extracting study data to ./study_data, this may take a moment\n\" && tar -xf /root/study_data.tar.xz -C /root/study_data --strip-components=1 --checkpoint=.4000 && rm /root/study_data.tar.xz && touch /root/study_data/.keep )"
printf "\nGenerating figures and printing tables to console\n"
docker-compose exec figs bash -c "cd /root/&& python3 figure_generator.py -full_data /root/study_data"