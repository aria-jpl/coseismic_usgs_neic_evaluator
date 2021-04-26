# coseismic_usgs_neic_evaluator
USGS NEIC evaluator

This repository contains code that will create a Program Executable (PGE) that generates HySDS datasets from USGS earthquake events. The PGE queries for acquisitions that overlap with the PDL event polygon then finds the union of the returned acquisitions for each track. The resulting polygon is published as an AOITRACK HySDS dataset. The overlap between these AOITRACKS and the extended PDL event polygon is published as an event AOI.

<img width="670" alt="Screen Shot 2021-04-26 at 10 51 45 AM" src="https://user-images.githubusercontent.com/47004511/116128092-6fb22200-a67d-11eb-84c0-160ccf08bf9f.png">

Users may add or modify regions by modifying the regions.json file. GeoJSON coordinates defining new regions may be appended to the collection of exisiting regions.

## Build Instructions

Built using the ARIA HySDS Jenkins Continuous Integration (CI) pipeline.

More information about this process can be found [here](https://hysds-core.atlassian.net/wiki/spaces/HYS/pages/455114757/Deploy+PGE+s+onto+Cluster)

Within the ARIA production environment, this PGE is built using the ARIA Jenkins server. You'll want to log onto the ARIA Mozart server and add / watch this repo first, then open up the Jenkins server in a browser and navigate to the project for this repo (which should show up after adding / watching this repo via the `sds ci ...` commands documented in the above link)

## Run Instructions

You may run your customized PGE via two methods that are documented below:
- An [on-demand (one-time) job](https://hysds-core.atlassian.net/wiki/spaces/HYS/pages/378601499/Submit+an+On-Demand+Job+in+Facet+Search)
- [Create a trigger rule](https://hysds-core.atlassian.net/wiki/spaces/HYS/pages/442728660/Create+Edit+Delete+Trigger+Rules) to invoke your PGE based on conditions

### USGS NEIC Event Evaluator PGE

- Name: `usgs_neic_event_evaluator`
- Condition:
```
{
  "bool": {
    "must": [
      {
        "term": {
          "dataset_type.raw": "event"
        }
      },
      {
        "term": {
          "dataset.raw": "usgs_neic_pdl_origin"
        }
      }
    ]
  }
}
```
- Action: `hysds-io-usgs_neic_event_evaluator:main`
- Queue: `factotum-job_worker-large`
- Keyword Args:
```
{
  "create_aoi_version": "master"
}
```

## Release History

`v1.0.0` - https://github.com/aria-jpl/coseismic_usgs_neic_evaluator/releases/tag/v1.0.0

## Contributing

1. Create an GitHub issue ticket describing what changes you need (e.g. issue-1)
2. Fork this repo (<https://github.com/aria-jpl/coseismic_usgs_neic_evaluator/fork>)
3. Make your modifications in your own fork
4. Make a pull-request in this repo with the code in your fork and tag the repo owner / largest contributor as a reviewer

## Support

Contact `@mlucas` for support.

