cities = \
	warszawa \
	krakow	\
	lodz \
	wroclaw \
	poznan \
	gdansk \
	szczecin \
	lublin \
	katowice \

day:
	make check-env
	make clean
	make preproc
	make crawl-all
	make report-all

preproc:
	echo "$$CITIES" > \
		python -m propertycrawl.preproc.dump_cities --jl \
		> out/$$JOB_START_DATE/cities.js

crawl-all:
	for city in $$(echo "$$CITIES" > python -m propertycrawl.preproc.dump_cities --env) ; \
	do \
		CITY=$$city KIND=wynajem make crawl-city ; \
		CITY=$$city KIND=sprzedaz make crawl-city ; \
	done

report-all:
	for city in $(cities) ; \
	do \
		CITY=$$city make report-city ; \
	done

crawl-city:
	mkdir -p out/$$JOB_START_DATE
	if [ "${KIND}" = "wynajem" ] ; then \
		scrapy crawl flats -a city=${CITY} -a kind=${KIND} -o out/$$JOB_START_DATE/${CITY}-rental.jl ; \
	fi
	if [ "${KIND}" = "sprzedaz" ] ; then \
		scrapy crawl flats -a city=${CITY} -a kind=${KIND} -o out/$$JOB_START_DATE/${CITY}-sales.jl ; \
	fi

report-city:
	python -m propertycrawl.postproc.overall_city_stats \
		out/$$JOB_START_DATE/${CITY}-rental.jl \
		out/$$JOB_START_DATE/${CITY}-sales.jl \
		> out/$$JOB_START_DATE/${CITY}-report-roi.jl 

clean:
	rm -rf out

upload-day:
	make check-env
	rm -rf .tmp
	mkdir -p .tmp/daily
	cp -r out/* .tmp/daily/
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
