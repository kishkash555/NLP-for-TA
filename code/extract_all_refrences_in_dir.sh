find -name "*.pdf" -print -exec curl -v --form input=@'{}'  -H "Accept: application/x-bibtex" localhost:8070/api/processReferences   \; > all_refs.txt

