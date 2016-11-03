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

job_start_date = $(shell date +%Y-%m-%d)

all:
	make check-env
	make crawl-all
	make report-all
	make plot-all

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

plot-all:
	for city in $(cities) ; \
	do \
		CITY=$$city make plot-city ; \
	done

crawl-city:
	mkdir -p out/$(job_start_date)
	if [ "${KIND}" == "wynajem" ] ; then \
		scrapy crawl flats -a city=${CITY} -a kind=${KIND} -o out/$(job_start_date)/${CITY}-rental.jl ; \
	fi
	if [ "${KIND}" == "sprzedaz" ] ; then \
		scrapy crawl flats -a city=${CITY} -a kind=${KIND} -o out/$(job_start_date)/${CITY}-sales.jl ; \
	fi

report-city:
	python -m propertycrawl.postproc.overall_city_stats_csv \
		out/$(job_start_date)/${CITY}-rental.jl \
		out/$(job_start_date)/${CITY}-sales.jl \
		> out/$(job_start_date)/${CITY}-report.csv 

plot-city:
	python -m propertycrawl.plots.barchart \
                ${CITY} \
		"District" \
		"ROI (%)" \
		out/$(job_start_date)/${CITY}-report.csv \
		out/$(job_start_date)/${CITY}-report-chart.html

	python -m propertycrawl.plots.map \
		out/$(job_start_date)/${CITY}-rental.jl \
		out/$(job_start_date)/${CITY}-sales.jl \
		out/$(job_start_date)/${CITY}-map-bg.png \
		out/$(job_start_date)/${CITY}-map-plot.html

check-env:
ifndef MAPBOX_ACCESS_TOKEN
	$(error MAPBOX_ACCESS_TOKEN is not set)
endif

