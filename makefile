format:
	black wifipumpkin3 setup.py

test:
	python3.7 -m unittest -v

test_coverage:
	python3.7 -m coverage run -m tests
	python3.7 -m coverage report
	python3.7 -m unittest -v

install:
	find . -name '*.pyc' -delete
	python3.7 setup.py install

install_env:
	python3.7 -m pip install PyQt5==5.14
	python3.7 -c "from PyQt5.QtCore import QSettings; print('done')"
	find . -name '*.pyc' -delete
	python3.7 setup.py install


install_dev:
	pip3 uninstall wifipumpkin3
	find . -name '*.pyc' -delete
	python3.7 setup.py install

clean:
	rm -rf build dist README MANIFEST *.egg-info
	python3.7 setup.py clean --all

distclean: clean
	rm -rf .venv
