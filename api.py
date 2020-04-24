#!/usr/bin/python
##########################################################
# Date: 20200425
# Objective: ManageEngine ServiceDesk Plus API
# Description: Automate ticket operation
###########################################################
import requests

API_token = "your-api-token"
baseurl = 'https://your-dashboard-url/api/v3/'
request_url = baseurl + 'requests/'

headers = {"Authtoken": API_token}

def get_requestID(request_url, headers, requestID):
  '''The requestID parameter is the ticket number defined, e.g. 1234567'''
  r = requests.get(request_url + str(requestID), headers=headers)
  if r.status_code == 200:
    content = r.json()
    # Print request result
    print "Requester: %s (%s)" %( content['request']['requester']['name'], content['request']['requester']['email_id'] )
    print "Request Time: %s" %( content['request']['created_time']['display_value'] )
    print "Subject: %s" %( content['request']['subject'] )
    print "Description: %s" %( content['request']['description'] )
    print "\n"
    if content['request']['technician']:
      print "Technician: %s (%s)" %( content['request']['technician']['name'], content['request']['technician']['email_id'] )
      print "Assign Time: %s" %( content['request']['assigned_time']['display_value'] )
    else:
      print "Technician: None"
      print "Assign Time: None"
    print "Group: %s" %( content['request']['group']['name'] )
    print "Status: %s" %( content['request']['status']['name'] )
    if content['request']['approval_status']:
      print "Approval Status: %s" %( content['request']['approval_status']['name'] )
    else: print "Approval Status: None"
    print "Due Time: %s" %(  content['request']['due_by_time']['display_value'])
  return r

def assign_requestID(request_url, headers, requestID, assignee, group):
  '''The assignee parameter has to be a full name defined e.g. Javier Moreno
     The group parameter has to be a group defined e.g. Infra Team'''
  assignment = {
         "request": {
           "group": {"name": group},
           "technician": {"name": assignee}
         }}
  data = {"input_data": str(assignment)}
  r = requests.put(request_url + str(requestID) + '/assign', headers=headers, data=data)
  if r.status_code is 200: print "%s assigned to %s" %( str(requestID), assignee )
  return r

def get_all_requests(request_url, headers):
  listInfo = {
    "list_info": {
      "row_count": "50",
      "start_index": "10",
      "sort_field": "subject",
      "sort_order": "asc",
      "get_total_count": "true",
      "search_fields": {
        "subject": "Infra",
        "priority.name": "high"
      }
    }
  }
  data = {"input_data": str(listInfo)}
  r = requests.get(request_url, headers=headers, data=data)
  
  content = r.json()
  interestedKeys = ['status','group','technician','created_time','requester','id','subject']
  
  tabulate_request(content, interestedKeys)
  
  return r

def close_requestID(request_url, headers, requestID, closureComments):
  closureInfo = {
    "request": {
      "closure_info": {
        "requester_ack_comments": "case resolved mutually",
        "closure_comments": closureComments
  }}}
  data = {"input_data": str(closureInfo)}
  r = requests.put(request_url + str(requestID) + '/close', headers=headers, data=data)
  return r

def delete_requestID(request_url, headers, requestID):
  '''Requests in Trash will be automatically deleted after 24 hours from the time of deletion'''
  r = requests.delete(request_url + str(requestID) + '/move_to_trash', headers=headers)
  if r.status_code is 200: print "%s is deleted successfully" %( str(requestID) )
  return r

def add_requestID(request_url, headers, subject=True, desc=False, requester=False, group=False):
  ticketInfo = {
    "request": {
      "subject": subject,
      "description": desc if desc else "Ticket for Infra request",
      "requester": {
        "name": requester if requester else "Javier Moreno"
      },
      "group": {
        "name": group if group else "Infra"
      },
      "status": {
        "name": "Open"
  }}}
  data = {"input_data": str(ticketInfo)}
  r = requests.post(request_url, headers=headers, data=data)
  if r.status_code is 201:
    content = r.json()
    print "Ticket %s %s is created to group %s" %( content['request']['id'], content['request']['subject'], content['request']['group']['name'] )
  return r

def tabulate_request(content, interestedKeys):
  '''The interestedKeys parameter defines a list of keys for the header of the table'''
  from prettytable import PrettyTable
  x = PrettyTable()
  x.field_names = interestedKeys
  for i in range(len( content['requests'] )):
    tmp = []
    for j in interestedKeys:
      if j is "status" or j is "group" or j is "requester": tmp.append( content['requests'][i][j]['name'] )
      elif j is "created_time": tmp.append( content['requests'][i][j]['display_value'] )
      elif j is "technician" and content['requests'][i][j]: tmp.append( content['requests'][i][j]['name'] )
      else: tmp.append( content['requests'][i][j] )
    x.add_row(tmp)
  print(x)
