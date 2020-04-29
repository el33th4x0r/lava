test:
	for i in test-[0-9][0-9]; do echo "$$i":; python3 lava.py "$$i"; done

clean:
	rm -f *~ parser.out

clobber: clean
	rm -rf parsetab.py __pycache__

