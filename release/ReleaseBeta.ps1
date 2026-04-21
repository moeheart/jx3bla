python -m release.GeneratorGenerator
python -m release.EquipmentTypeGenerator
python -m release.JsonGenerator
python -m release.NameGenerator
git add *.py *.md *.spec release/*.ps1 release/*.md
git commit -m "[Auto]Update as the log"
git push origin
pyinstaller MainWindow.beta.spec
mv dist/MainWindow.exe dist/j3jz-beta.exe
