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

all:
	make check-env
	make clean
	make crawl-all
	make report-all

crawl-all:
	for city in $(cities) ; \
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

check-env:
ifndef JOB_START_DATE
	$(error JOB_START_DATE is not set)
endif
