from pkg_resources import declare_namespace
declare_namespace('csvimport')
import csvimport.monkeypatch_tzinfo
# Allow for the management commands to import these ...
import parser, make_model
