from django import dispatch

imported_csv = dispatch.Signal(providing_args=['instance', 'row'])
importing_csv = dispatch.Signal(providing_args=['instance', 'row'])
