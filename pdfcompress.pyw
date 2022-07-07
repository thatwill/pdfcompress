import os
import sys
import tempfile
import shutil
import builtins
import wx

# set ghostscript DLL dir (for Windows 64-bit only)
if os.name == 'nt':
  builtins.ghostscript_PATH_TO_DLL = os.getcwd()+'\gsdll64.dll'

import ghostscript

app = wx.App()

if len(sys.argv)==2:
  # get original PDF path name from command line argument
  pathOriginal = os.path.abspath(sys.argv[1])
else:
  # or get from a dialog box
  fileDialog = wx.FileDialog(None,message="Select a PDF to compress",wildcard="PDF files (.pdf)|*.pdf",style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
  if fileDialog.ShowModal()==wx.ID_CANCEL:
      sys.exit()
  else:
      pathOriginal = fileDialog.GetPath()

if pathOriginal:
  # ensure file given exists, is PDF, and directory has read/write access
  dirpath = os.path.dirname(pathOriginal)
  if os.path.isfile(pathOriginal) and os.path.splitext(pathOriginal)[1]==".pdf" and os.access(dirpath, os.W_OK) and os.access(dirpath, os.R_OK):

    # generate new PDF filename (same directory with _sm.pdf suffix)
    filename = os.path.basename(pathOriginal)

    filenameNew = os.path.splitext(filename)[0]+"_sm.pdf"
    pathNew = os.path.join(dirpath,filenameNew)

    # show progress bar dialog
    msg = ''' PDF compression in progress...
        Original file: {0}
        New file: {1}'''
    msg = msg.format(filename,filenameNew)
    
    dlgProgress = wx.ProgressDialog(title="PDF Compression",message=msg,style=wx.PD_AUTO_HIDE)
    dlgProgress.Pulse()
                      
    # copy PDF to temp file
    pathTempOrig = tempfile.NamedTemporaryFile().name
    shutil.copy2(pathOriginal,pathTempOrig)
    
    pathTempNew = tempfile.NamedTemporaryFile().name

    # run ghostscript using the "ebook" preset to compress the PDF
    args = [
        "gs",
        "-dQUIET","-dBATCH","-dNOPAUSE","-dSAFER",
        "-sDEVICE=pdfwrite","-dPDFSETTINGS=/ebook",
        "-sOutputFile=" + pathTempNew,
        pathTempOrig
    ]
    ghostscript.Ghostscript(*args)

    # Copy to new location and delete temp files
    shutil.copy2(pathTempNew,pathNew)
    os.remove(pathTempOrig)
    os.remove(pathTempNew)
    
    dlgProgress.Update(100) # close progress dialog
    
    dlg = wx.MessageDialog(None, "Compression is completed. New filename:\n"+pathNew, "PDF Compression Complete", wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()
  else:
      dlg = wx.MessageDialog(None, "Invalid file or directory.\nFile must exist, be a PDF, and you must have the ability to read and write files to this location.\n"+pathOriginal, "PDF Compression", wx.OK | wx.ICON_ERROR)
      dlg.ShowModal()
      dlg.Destroy()
sys.exit()
