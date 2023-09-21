format:
	black wifipumpkin3 setup.py

test:
	python3 -m unittest -v

test_coverage:
	python3 -m coverage run -m tests
	python3 -m coverage report
	python3 -m unittest -v

install:
	find . -name '*.pyc' -delete
	python3 -m pip install .

install_env:
	python3 -m pip install PyQt5==5.14
	python3 -c "from PyQt5.QtCore import QSettings; print('done')"
	find . -name '*.pyc' -delete
	python3 -m pip install .


install_dev:
	pip3 uninstall wifipumpkin3
	find . -name '*.pyc' -delete
	python3 -m pip install .

clean:
	rm -rf build dist README MANIFEST *.egg-info
	python3 setup.py clean --all

distclean: clean
	rm -rf .venv
