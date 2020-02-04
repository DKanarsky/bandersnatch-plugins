# bandersnatch-plugins
Plugins for [bandersnatch](https://github.com/pypa/bandersnatch) a PyPI mirror client 

##  whitelist_release_pyversion

Use this plugin to filter python versions. For example:
```uml
[plugins]
enabled =
  whitelist_release_pyversion

[whitelist]
python_versions =
  source
  any
  cp37
  py2.py3
  py3
  py3.7
  python
```

##  filter_release

This plugin combines **latest_release** with selecting specific releases to download (in addition to the latest releases). 
For example:

```uml
[plugins]
enabled =
  filter_release

[filter_release]
keep = 1
releases =
  numpy==1.17.2
  tensorboard==1.14.0
  tensorflow-estimator==1.14.0rc1
  gast==0.2.2
```

*Note that plugin's order in config makes sense. Actualy, mixing different plugins may lead to unexpected results*
