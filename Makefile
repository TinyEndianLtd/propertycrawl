all:
	make check-env
	make clean
	make preproc
	make crawl
	make postproc

preproc:
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

crawl-city:
	mkdir -p out/$$JOB_START_DATE/data
	if [ "${KIND}" = "wynajem" ] ; then \
		scrapy crawl flats -a city=${CITY} -a kind=${KIND} -o out/$$JOB_START_DATE/${CITY}-rental.jl ; \
	fi
	if [ "${KIND}" = "sprzedaz" ] ; then \
		scrapy crawl flats -a city=${CITY} -a kind=${KIND} -o out/$$JOB_START_DATE/${CITY}-sales.jl ; \
	fi

report-city:
	mkdir -p out/$$JOB_START_DATE/reports
	python -m propertycrawl.postproc.overall_city_stats \
		out/$$JOB_START_DATE/data/${CITY}-rental.jl \
		out/$$JOB_START_DATE/data/${CITY}-sales.jl \
		> out/$$JOB_START_DATE/reports/${CITY}-report-roi.jl

clean:
	rm -rf out

upload:
	rm -rf .tmp
	mkdir -p .tmp/daily
	cp -r out/input/* .tmp/daily/
	cp -r out/data/* .tmp/daily/
	cd .tmp && aws s3 sync . s3://$$BUCKET_NAME
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