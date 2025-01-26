from csvTOrdfv2 import CSV2RDF, namespace, function_generate_rdf

dataFolderPath = "../data"
outputFolderPath = "../output"
rdfFileName = "output_og_24.ttl"
csvFileName = "medal_og_24.csv"
overwriteFiles = "All"
csvFileEncoding = "utf-8-sig"




file = "athlete"

if "medal" == file :
    csvFileName = "medal_og_24.csv"
    overwriteFiles = "All"
    csvFileEncoding = "utf-8-sig"

if "athlete" == file :
    csvFileName = "athlete_og_24.csv"
    overwriteFiles = None
    csvFileEncoding = "utf-8-sig"



csv2rdf = CSV2RDF(dataFolderPath, outputFolderPath, csvFileName, rdfFileName, overwriteFiles, csvFileEncoding)
csv2rdf.create_rdf(namespace, function_generate_rdf)