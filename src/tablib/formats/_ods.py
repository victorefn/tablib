""" Tablib - ODF Support.
"""

from io import BytesIO

from odf import opendocument, style, table, text

bold = style.Style(name="bold", family="paragraph")
bold.addElement(style.TextProperties(fontweight="bold", fontweightasian="bold", fontweightcomplex="bold"))


class ODSFormat:
    title = 'ods'
    extensions = ('ods',)

    @classmethod
    def export_set(cls, dataset):
        """Returns ODF representation of Dataset."""

        wb = opendocument.OpenDocumentSpreadsheet()
        wb.automaticstyles.addElement(bold)

        ws = table.Table(name=dataset.title if dataset.title else 'Tablib Dataset')
        wb.spreadsheet.addElement(ws)
        cls.dset_sheet(dataset, ws)

        stream = BytesIO()
        wb.save(stream)
        return stream.getvalue()

    @classmethod
    def export_book(cls, databook):
        """Returns ODF representation of DataBook."""

        wb = opendocument.OpenDocumentSpreadsheet()
        wb.automaticstyles.addElement(bold)

        for i, dset in enumerate(databook._datasets):
            ws = table.Table(name=dset.title if dset.title else 'Sheet%s' % (i))
            wb.spreadsheet.addElement(ws)
            cls.dset_sheet(dset, ws)

        stream = BytesIO()
        wb.save(stream)
        return stream.getvalue()

    @classmethod
    def dset_sheet(cls, dataset, ws):
        """Completes given worksheet from given Dataset."""
        _package = dataset._package(dicts=False)

        for i, sep in enumerate(dataset._separators):
            _offset = i
            _package.insert((sep[0] + _offset), (sep[1],))

        for i, row in enumerate(_package):
            row_number = i + 1
            odf_row = table.TableRow(stylename=bold, defaultcellstylename='bold')
            for j, col in enumerate(row):
                try:
                    col = str(col, errors='ignore')
                except TypeError:
                    ## col is already str
                    pass
                ws.addElement(table.TableColumn())

                # bold headers
                if (row_number == 1) and dataset.headers:
                    odf_row.setAttribute('stylename', bold)
                    ws.addElement(odf_row)
                    cell = table.TableCell()
                    p = text.P()
                    p.addElement(text.Span(text=col, stylename=bold))
                    cell.addElement(p)
                    odf_row.addElement(cell)

                # wrap the rest
                else:
                    try:
                        if '\n' in col:
                            ws.addElement(odf_row)
                            cell = table.TableCell()
                            cell.addElement(text.P(text=col))
                            odf_row.addElement(cell)
                        else:
                            ws.addElement(odf_row)
                            cell = table.TableCell()
                            cell.addElement(text.P(text=col))
                            odf_row.addElement(cell)
                    except TypeError:
                        ws.addElement(odf_row)
                        cell = table.TableCell()
                        cell.addElement(text.P(text=col))
                        odf_row.addElement(cell)

    @classmethod
    def detect(cls, stream):
        if isinstance(stream, bytes):
            # load expects a file-like object.
            stream = BytesIO(stream)
        try:
            opendocument.load(stream)
            return True
        except Exception:
            return False
