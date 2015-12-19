#OpenResource

### About
OpenResource is a resource reservation system. 
Registered users can create their own resources and provide availability times for other users to reserve.
Users can see a list of all resources in the system and request reservation times during listed availabilities. 

We hope our application encourages the use of resource sharing and<br> eventually hope to expand to allow community groups to form their own resource sharing ecosystem through our system.

&copy; 2015 Jasmine Hsu 

### Main Page
There are three sections on the main page
## User Reservations
All resources you created. 
- Click the info icon to see resource details. 
- Click the user icon to see user details. 
- Click the trash icon to trash your reservation
Reservations are sorted from most immediate to later.
Reservations will be deleted after the reservation end time has past. 
Time is currently hardcoded to be based on  US/Eastern

## User Owned Resources
All resources you created. 
- Click the info icon to see resource details. 
- Click the pencil icon to edit resource details. 
- Click the export icon to see resource RSS feed.

## Available Resources
All available resources in the system. 
- Click the info icon to see resource details. 
- Click the bookmark icon to reserve the resource.
- Click the user icon to see user resource details. 
- Click the export icon to see resource RSS details. 

You can't reserve your own resource. 
Instead you will be able to edit it. 
Your own resource will be indicated with an "owner" tag. 
Resources are sorted by last made rsvp. 
After you make a new reservation, you must refresh to 
see the change in the sort order.

### Add a resource
Create a resource by including
- Resource name
- Date
- Start time
- End time
- List of tags

Note: We only validate date, start and end times.
Resource names do not have to be unique (i.e. multiple
resources can have the same name). Resources
are identified by their generated resource keys.

### Resource Details Page
See resource details
- Resource name
- Resource availability (Date, start, end time)
- Resource tags
On this page you can edit / bookmark or export RSS feeds.
It will show existing reservations for this resource.
The last panel you can choose to search for other resources
that are tagged with the same label. Choose the tag
you want to search for in the dropdown.
The dropdown will only list tags that are in the current
resource whose page you are on.

### User Details Page
You will see a list of user created reservations
and user created resources.

Reservations older than current time will not be shown.

Page format is similiar to main page.

### Create Reservation Page
Fill out the form to create a reservation
given the resource availability as listed.

Start and end time will be validated against
resource availability.

This page will show existin reservations for the
resource if it exists. You must request a time
outside of conflicting reservations.

The next page will alert with a alert panel on the
top of the page whether a reservation was successfully
created.  If it is not successful it is because
the reservation request conflicts with existing
reservations.

### Thanks. 





