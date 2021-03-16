find -name "*.pdf" -print -exec curl -v --form input=@'{}'  -H "Accept: application/x-bibtex" localhost:8070/api/processReferences   \; > all_refs.txt

find . -name "*.pdf" | xargs -I % sh -c "curl -v --form input=@'%'  localhost:8070/api/processHeaderDocument > '../review_revenue_header_xml/%.xml'"

