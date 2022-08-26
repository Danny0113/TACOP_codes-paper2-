

def dominates(row, candidateRow):
    return sum([row[x] <= candidateRow[x] for x in range(len(row))]) == len(row)


def simple_cull(inputPoints, dominates):
    paretoPoints = set()
    candidateRowNr = 0
    dominatedPoints = set()
    while True:
     candidateRow = inputPoints[candidateRowNr]
     inputPoints.remove(candidateRow)
     rowNr = 0
     nonDominated = True
     while len(inputPoints) != 0 and rowNr < len(inputPoints):
      row = inputPoints[rowNr]
      if dominates(candidateRow, row):
       # If it is worse on all features remove the row from the array
       inputPoints.remove(row)
       dominatedPoints.add(tuple(row))
      elif dominates(row, candidateRow):
       nonDominated = False
       dominatedPoints.add(tuple(candidateRow))
       rowNr += 1
      else:
       rowNr += 1

     if nonDominated:
      # add the non-dominated point to the Pareto frontier
      paretoPoints.add(tuple(candidateRow))

     if len(inputPoints) == 0:
      break
    return paretoPoints, dominatedPoints


if __name__ == '__main__':
    inputPoints = [[0, 0, 0], [1, 4, 1], [0.3296170319979843, 0.0, 0.44472108843537406], [0.3296170319979843,0.0, 0.44472108843537406], [0.32920760896951373, 0.0, 0.4440408163265306], [0.32920760896951373, 0.0, 0.4440408163265306], [0.33815192743764166, 0.0, 0.44356462585034007]]
    paretoPoints, dominatedPoints = simple_cull(inputPoints, dominates)
