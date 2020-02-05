conda build .
conda install --use-local -y --force-reinstall hexmap
conda build purge
