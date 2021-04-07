git add *.py *.md
git commit -m "[Auto]Update as the log"
git push origin
pyinstaller -F -i jx3bla.ico MainWindow.py
mv dist/MainWindow.exe dist/剑三警长v$args.exe