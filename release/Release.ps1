git add *.py *.md
git commit -m "[Auto]Update as the log"
git push origin
pyinstaller -F -i jx3bla.ico MainWindow.py
mkdir dist/publish
mv dist/MainWindow.exe dist/publish/j3jz.exe
cp -r icons dist/publish/