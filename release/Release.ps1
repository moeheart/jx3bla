python release/GeneratorGenerator.py
python release/EquipmentTypeGenerator.py
python release/JsonGenerator.py
python release/NameGenerator.py
python release/PercentGenerator.py
git add *.py *.md
git commit -m "[Auto]Update as the log"
git push origin
pyinstaller -F -i jx3bla.ico MainWindow.py
mv dist/MainWindow.exe dist/j3jz.exe
# mkdir dist/publish
# mv dist/MainWindow.exe dist/publish/j3jz.exe
# cp -r icons dist/publish/
