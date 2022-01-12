for %%f in (%2\*.xml) do (
    XmlMethodChanger -i %1 -m %f -o %3\%%~nf.meth
)
