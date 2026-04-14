1- setup the python virtual environment 
>> python -m venv venv

2- activate the venv
>> venv\Scripts\activate

FLAGS for the command to avail the features 

Flag,Short,Description
--sort-by type,  -s type,   Sort by file extension
--sort-by size,  -s size,  Sort by file size
--sort-by date,  -s date,  Sort by modified date
--dry-run,-d,  "Preview only,   no files moved"
--recursive,  -r,  Include subfolders
--undo,  -u,  Reverse last run
--config,  -c,  Use a custom config.yaml path


HOW TO RUN THE PROJECT 
>> python main.py path_to_directory/name_of_directory flag_feature_command

