if ! command -v docker-compose &> /dev/null
then
    echo "docker-compose could not be found. This script relies on the original docker-compose rather than docker compose."
    echo "docker-compose can be installed as follows:"
    echo "sudo curl -L \"https://github.com/docker/compose/releases/download/1.28.5/docker-compose-$(uname -s)-$(uname -m)\" -o /usr/local/bin/docker-compose"
    echo "sudo chmod +x /usr/local/bin/docker-compose"
    exit
fi

printf "Setting up Docker container\n"
docker-compose up --build -d
printf "Checking if study data has been downloaded\n"
docker-compose exec figs bash -c "mkdir /root/study_data 2>/dev/null"
docker-compose exec figs bash -c "test -f \"/root/study_data/.keep\" && printf \"Files already downloaded\n\" || ( wget -O /root/study_data.tar.xz https://zenodo.org/record/7569212/files/study_data_compressed.tar.xz?download=1 && printf \"Extracting study data to ./study_data, this may take a moment\n\" && tar -xf /root/study_data.tar.xz -C /root/study_data --strip-components=1 --checkpoint=.4000 && rm /root/study_data.tar.xz && touch /root/study_data/.keep )"
printf "\nGenerating figures and printing tables to console\n"
docker-compose exec figs bash -c "cd /root/&& python3 figure_generator.py -full_data /root/study_data"