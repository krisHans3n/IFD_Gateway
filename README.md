# IFD_Gateway
API gateway for fraudulent image detection microservices



-----------------------------------------------------------------------------------------

- worker spawn / dispatch module
- worker diagnostics
- runtime services table
- routing map
- request interperator 
- json validation
- failure handler
- feed forward handler (client updates)
- instance handler
- token authenticaor
- database initialiser (set-up for both redis and sqlite)
- runtime manager
- runtime cleaner

-----------------------------------------------------------------------------------------

Post URLs
Validate URL string
Instantiate dispatcher
    - check api list for live apis
         - add api addresses to list and pass to dispatcher
         - generate guid (guid will be used to gather responses)
    - dispatch to api 1 / 2 / ..n
    - map dispatch job request to guid
         - store in object dict
    - after dispatch all:
         - loop through job ids and check complete
         - check for max 2 minutes before timeout
         - when all jobs complete instantiate merge class
              - if response less than specific size (e.g. 1 mb)
                   - store json in memory with shared dict (preferibly redis if host provides)
              - api request responses to be stored as JSONB in postgresql db
                   - psql db necessary for prototype host heroku
              - search db for responses
    
    




