import sys

import win32com.client as win32

print("This is the name of the program:", sys.argv[0])

print("Argument List:", str(sys.argv))


outlook = win32.Dispatch("outlook.application")
mail = outlook.CreateItem(0)
# Must write some destination mail address here
mail.To = ""
mail.Subject = "Alteryx Combine Two Sheets Alert"
mail.Body = "Hello from python\n" + str(sys.argv[1])
# mail.HTMLBody = "<h2>Title</h2>"
# attachment = "Path to the attachment"
# mail.Attachments.Add(attachment)
mail.Send()
