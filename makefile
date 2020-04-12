format:
	black wifipumpkin3 setup.py

test:
	python3.7 -m coverage run -m tests
	python3.7 -m coverage report
	python3.7 -m unittest -v

setup:
	python3.7 setup.py install

clean:
	rm -rf build dist README MANIFEST *.egg-info
	python3.7 setup.py clear --all

distclean: clean
	rm -rf .venv