import sys, csv, json, wppbatchlib

VERSION = '0.1'
AUTHOR = 'Trevor Anderson <tanderson@whitepages.com>'

try:
	iFilePath = None
	resultsFilePath = None

	if sys.argv == None or len(sys.argv) != 2 or len(sys.argv[1]) < 5 or sys.argv[1][-14:] != 'rawresults.csv':
		print 'Drop a CSV file containing raw JSON results onto this program to use it.'
		print '(you need to run SearchPhone.bat first)'
		var = raw_input("Hit enter to quit")
		quit()
	
	iFilePath = sys.argv[1]
	resultsFilePath = sys.argv[1][:-15]+'_results.csv'
	print 'Extracting Phone Reputation results from '+str(iFilePath)
	
	csvReader = csv.reader(open(iFilePath,'rb'), delimiter=',', quotechar = '"')
	csvWriter = csv.writer(open(resultsFilePath,'wb'),delimiter=',',quotechar='"')
	
	rowNum = 0
	for row in csvReader:
		#each raw results row will contain the original input file row, followed by the API URL,
		#followed by the JSON response.
		rowNum += 1
		if rowNum == 1:
			csvWriter.writerow(row[:-2]+['Error','Reputation Level','Reputation Details','Report Count','Volume Score'])
		else:
			data = {}
			try:
				data = json.loads(row[-1])
			except:
				print 'Error reading JSON on row '+str(rowNum)
				csvWriter.writerow(row[:-2]+['Failed to load JSON results','','','',''])
				continue
			
			error = wppbatchlib.nvl(data.get('error',{}),{}).get('message','')
			results = wppbatchlib.nvl(data.get('results',[{}]),[{}])[0]
			rep = results.get('reputation',{})
			repLevel = rep.get('level','')
			repVolume = rep.get('volume_score',0)
			repReport = rep.get('report_count',0)
			repDetails = ''
			numDetails = 0
			for x in rep.get('details',[]):
				numDetails += 1
				if numDetails > 1:
					repDetails += '|'
				repDetails += x.get('type','')
				repDetails += ';'
				repDetails += x.get('category','')
				repDetails += ';'
				repDetails += str(x.get('score',''))
			csvWriter.writerow(row[:-2]+[error,repLevel,repDetails,repReport,repVolume])
	
	print 'All done!'
	print 'You can find your results file here: '+str(resultsFilePath)
	print ''
except:
	print 'An unknown error occurred: '+str(sys.exc_info()[0])