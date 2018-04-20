all:
	make check-env
	make clean
	make preproc
	make crawl
	make postproc

preproc:
	yarn run proxy-lists getProxies --sources-white-list=$$PROXIES_SOURCE_LIST
	mkdir -p out/$$JOB_START_DATE/input
	echo "$$CITIES" | python -m propertycrawl.preproc.dump_cities --jl > out/$$JOB_START_DATE/input/cities.jl

crawl:
	for city in $$(echo "$$CITIES" | python -m propertycrawl.preproc.dump_cities --env) ; \
	do \
		CITY=$$city KIND=wynajem make crawl-city ; \
		CITY=$$city KIND=sprzedaz make crawl-city ; \
	done

postproc:
	for city in $$(echo "$$CITIES" | python -m propertycrawl.preproc.dump_cities --env) ; \
	do \
		CITY=$$city make report-city ; \
	done
	mkdir -p out/$$JOB_START_DATE/reports/alltime
	mkdir -p .tmp
	if aws s3 cp s3://$$BUCKET_NAME/latest/all-cities.jl .tmp/all-cities-to-date.jl ; \
	then \
		cat .tmp/all-cities-to-date.jl out/$$JOB_START_DATE/input/cities.jl | python -m propertycrawl.postproc.aggregated_cities $$JOB_START_DATE > out/$$JOB_START_DATE/reports/alltime/all-cities.jl ; \
	else \
		cat out/$$JOB_START_DATE/input/cities.jl | python -m propertycrawl.postproc.aggregated_cities $$JOB_START_DATE > out/$$JOB_START_DATE/reports/alltime/all-cities.jl ; \
	fi
	rm -r .tmp

crawl-city:
	mkdir -p out/$$JOB_START_DATE/data
	if [ "${KIND}" = "wynajem" ] ; then \
		scrapy crawl flats -a city=${CITY} -a kind=${KIND} -o out/$$JOB_START_DATE/data/${CITY}-rental.jl ; \
	fi
	if [ "${KIND}" = "sprzedaz" ] ; then \
		scrapy crawl flats -a city=${CITY} -a kind=${KIND} -o out/$$JOB_START_DATE/data/${CITY}-sales.jl ; \
	fi

report-city:
	mkdir -p out/$$JOB_START_DATE/reports/daily
	python -m propertycrawl.postproc.daily_city_report \
		out/$$JOB_START_DATE/data/${CITY}-rental.jl \
		out/$$JOB_START_DATE/data/${CITY}-sales.jl \
		> out/$$JOB_START_DATE/reports/daily/${CITY}-report.jl

clean:
	rm -f proxies.txt
	rm -rf out

upload:
	rm -rf .tmp
	mkdir -p .tmp/daily/$$JOB_START_DATE/
	cp -r out/$$JOB_START_DATE/input/* .tmp/daily/$$JOB_START_DATE/
	cp -r out/$$JOB_START_DATE/data/* .tmp/daily/$$JOB_START_DATE/
	cp -r out/$$JOB_START_DATE/reports/daily/* .tmp/daily/$$JOB_START_DATE/
	cp -r out/$$JOB_START_DATE/reports/alltime/* .tmp/daily/$$JOB_START_DATE/
	cd .tmp && aws s3 sync . s3://$$BUCKET_NAME
	aws s3 sync s3://$$BUCKET_NAME/daily/$$JOB_START_DATE/ s3://$$BUCKET_NAME/latest/
	rm -rf .tmp

check-env:
ifndef CITIES
	$(error CITIES is not set)
endif
ifndef JOB_START_DATE
	$(error JOB_START_DATE is not set)
endif
ifndef BUCKET_NAME
	$(error BUCKET_NAME is not set)
endif
ifndef PROXIES_SOURCE_LIST
	$(error PROXIES_SOURCE_LIST is not set)
endif
