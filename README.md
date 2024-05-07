# childInTime.py
This is a python module that encodes / decodes strings representing date and
time.
It is written for Python 3.2.5.1 being the latest version of python usable
under Windows XP.
The strongest feature of childInTime stays in the versatility of the format
used to describe the six types of integers you may find in a string with a
time-related value:

  * Years, Months, Days
  * Hours, Minutes, Seconds

The childInTime module is a _naive_ date and time object in the Python sense,
as it ignores time zone information. Further more, it igores some
_common sense_ restrictions as 24 hour long days and a maximum of 31 days in a
month. Some restrictions remain, as you can have up to 4 digits for years and
1 or two digits for the rest of the fields. The general format looks like this:
```code
YYYY:delim:MM:delim:DD[:whitesp:]HH:delim:MM:delim:SS[:whitesp:]AM/PM
```

Where `:whitesp:` stands for white space and `:delim:` is a one character long
delimiter of your choice. Any of the six fields (years `YYYY`, months `MM`,
days `DD`, hours `HH`, minutes `MM` or seconds `SS`), could be missing, the
same stands for the `AM/PM` placeholder. Also the order of the fields is
optional, but for example it's better to keep the date fields (`Y[Y[Y[Y]]]`,
`M[M]`, `D[D]`) closer together especially when there is ambiguity about
wether the `M[M]` field stands for minutes or months. Same reasoning regarding
the time fields.

This module can decipher any format string as long as
it contains at least two of the `Y[Y[Y[Y]]]`, `M[M]`, `D[D]`, `H[H]`, and
`S[S]` tokens along with the optional `AM/PM` placeholder. Some restrictions
apply, as for example you cannot use the `AM/PM` placeholder if the hour token
is missing.


## Usage:

The main purpose of this module is to _translate_ a string representing a
time-related value from a format to another.

For this you will need two
formats. For example let's assume that your input data comes in this format:
`H:MM AM/PM` and that you want to output the data in this format: `HH:MM`.

a sample usage of the code would look like this:
```code
from childInTime import somewhereInTime

inputMoment = somewhereInTime('H:MM AM/PM', 'time')
outMoment = somewhereInTime('HH:MM', 'time')

startStr = '12:20 AM'

inputMoment.decodeString(startStr)

outMoment.setHour(inputMoment.getHour())
outMoment.setMinute(inputMoment.getMinute())

endStr = outMoment.encodeToString()

print('startStr:', startStr )
print('endStr:', endStr )
```
The output of the code above looks like this:


```
startStr: 12:20 AM
endStr: 00:20
```

