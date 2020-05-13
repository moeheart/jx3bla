from main import DpsGeneralStatGenerator

filename = "2020-05-13-20-43-07_铁黎_377.fstt.jx3dat"

dpsGenerator = DpsGeneralStatGenerator(filename)
dpsStat = dpsGenerator.SecondStageAnalysis()
print(dpsStat)