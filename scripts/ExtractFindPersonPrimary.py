import sys, csv, json, wppbatchlib
csv.field_size_limit(min(2147483647,sys.maxsize))

VERSION = '0.1'
AUTHOR = 'Trevor Anderson <tanderson@whitepages.com>'


iFilePath = None
resultsFilePath = None

if sys.argv == None or len(sys.argv) != 2 or len(sys.argv[1]) < 5 or sys.argv[1][-14:] != 'rawresults.csv':
	print 'Drop a CSV file containing raw JSON results onto this program to use it.'
	print '(you need to run SearchPerson.bat first)'
	var = raw_input("Hit enter to quit")
	quit()

iFilePath = sys.argv[1]
resultsFilePath = sys.argv[1][:-15]+'_results.csv'
print 'Extracting Find Person results from '+str(iFilePath)

csvReader = csv.reader(open(iFilePath,'rbU'), delimiter=',', quotechar = '"')
csvWriter = csv.writer(open(resultsFilePath,'wb'),delimiter=',',quotechar='"')

rowNum = 0
for row in csvReader:
	#each raw results row will contain the original input file row, followed by the API URL,
	#followed by the JSON response.
	rowNum += 1
	
	if rowNum == 1:
		headers = ['Error']
		headers.append('Result Number')
		headers.append('First Name')
		headers.append('Middle Name')
		headers.append('Last Name')
		headers.append('Age Range')
		headers.append('Gender')
		headers.append('Location Is Historical')
		headers.append('Location Type')
		headers.append('Location Valid From')
		headers.append('Location Valid To')
		headers.append('Street')
		headers.append('City')
		headers.append('State')
		headers.append('Postal Code')
		headers.append('Zip+4')
		headers.append('Country')
		headers.append('Location Delivery Point')
		headers.append('Location Usage Type')
		headers.append('Location Receiving Mail')
		headers.append('Location LatLon Accuracy')
		headers.append('Location Latitude')
		headers.append('Location Longitude')
		headers.append('Landline Phone')
		csvWriter.writerow(row[:-2]+headers)
	else:
		data = {}
		try:
			data = json.loads(row[-1])
		except:
			print 'Error reading JSON on row '+str(rowNum)
			csvWriter.writerow(row[:-2]+['Failed to load JSON results','','','',''])
			continue
		
		error = wppbatchlib.nvl(data.get('error',{}),{}).get('message','')
		results = wppbatchlib.nvl(data.get('results',[{}]),[{}])
					
							
		if error == '' and len(results[0].keys()) == 0:
			error = 'No results found'
		
		resultNum = 0
		for primaryPerson in results:
			primaryPersonKey = primaryPerson.get('id',{}).get('key')
			resultNum += 1
			
			locs = primaryPerson.get('locations',[{}])
			
			for location in locs:
					
				isHistorical = location.get('is_historical','')	
				locType = location.get('type','')
				start = wppbatchlib.nvl(wppbatchlib.nvl(location.get('valid_for',{}),{}).get('start',{}),{})
				end = wppbatchlib.nvl(wppbatchlib.nvl(location.get('valid_for',{}),{}).get('stop',{}),{})
				validFrom = str(start.get('year',''))+'-'+str(start.get('month',''))+'-'+str(start.get('day',''))
				validTo = str(end.get('year',''))+'-'+str(end.get('month',''))+'-'+str(end.get('day',''))	
				
				street = location.get('standard_address_line1','')
				city = location.get('city','')
				state = location.get('state_code','')
				postalCode = location.get('postal_code','')
				zip4 = location.get('zip4','')
				country = location.get('country_code','')
				deliveryPoint = location.get('delivery_point','')
				usageType = location.get('usage','')
				rcvMail = location.get('is_receiving_mail','')
				
				latLonAccuracy = wppbatchlib.nvl(location.get('lat_long',{}),{}).get('accuracy','')
				latitude = wppbatchlib.nvl(location.get('lat_long',{}),{}).get('latitude','')
				longitude = wppbatchlib.nvl(location.get('lat_long',{}),{}).get('longitude','')
				
				#fetch people, but only get the primary person
				for person in location.get('legal_entities_at',[{}]):
					personKey = person.get('id',{}).get('key')
					if personKey != primaryPersonKey:
						continue
						
					personName = wppbatchlib.nvl(person.get('names',[{}]),[{}])[0]
					firstName = personName.get('first_name','')
					middleName = personName.get('middle_name','')
					lastName = personName.get('last_name','')
					ageRange = str(wppbatchlib.nvl(person.get('age_range',{}),{}).get('start','?'))
					ageRange +='-'+str(wppbatchlib.nvl(person.get('age_range',{}),{}).get('end','?'))
					if ageRange == '?-?':
						ageRange = ''
					gender = person.get('gender','')
					
					phoneNumber = ''
					phones = wppbatchlib.nvl(primaryPerson.get('phones',[{}]),[{}])
					if phones is not None:
						for p in phones:
							phoneNumber = p.get('phone_number','')
							break
				
					resultRow = [error]
					resultRow.append(resultNum)
					resultRow.append(firstName)
					resultRow.append(middleName)
					resultRow.append(lastName)
					resultRow.append(ageRange)
					resultRow.append(gender)
					resultRow.append(isHistorical)
					resultRow.append(locType)
					resultRow.append(validFrom)
					resultRow.append(validTo)
					resultRow.append(street)
					resultRow.append(city)
					resultRow.append(state)
					resultRow.append(postalCode)
					resultRow.append(zip4)
					resultRow.append(country)
					resultRow.append(deliveryPoint)
					resultRow.append(usageType)
					resultRow.append(rcvMail)
					resultRow.append(latLonAccuracy)
					resultRow.append(latitude)
					resultRow.append(longitude)
					resultRow.append(phoneNumber)
					
					csvWriter.writerow(row[:-2]+resultRow)

print 'All done!'
print 'You can find your results file here: '+str(resultsFilePath)
print ''
	