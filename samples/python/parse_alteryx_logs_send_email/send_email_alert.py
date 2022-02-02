import re
import sys

import win32com.client as win32


def parse_messages(text):
    groups = re.findall(r"(?<=)'message':(.*?)},", text)
    return groups


def parse_workflow_path(text):
    groups = re.findall(r"(?<=)'workflow_path':(.*?),", text)
    return groups


text = str(sys.argv[1])
workflow_path = parse_workflow_path(text)
messages = parse_messages(text)


outlook = win32.Dispatch("outlook.application")
mail = outlook.CreateItem(0)
# Must write some destination mail address here
mail.To = ""
mail.Subject = "Alteryx Combine Two Sheets Alert"
# Message
# mail.Body = "Hello from python\n" + str(sys.argv[1])
mail.HTMLBody = f"""
<h1>Alteryx Workflow Alert</h1>

Workflow path: {workflow_path}

</br>

<h2>Logs</h2>
{"</br> ".join(messages)}

"""
# attachment = "Path to the attachment"
# mail.Attachments.Add(attachment)
mail.Send()
