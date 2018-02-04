base9 = '123456789'  # The first digit (after the "N") is always one of these.
base10 = '0123456789' # The possible second and third digits are one of these.
# Note that "I" and "O" are never used as letters, to prevent confusion with "1" and "0"
base34 = 'ABCDEFGHJKLMNPQRSTUVWXYZ0123456789'
icaooffset = 0xA00001 # The lowest possible number, N1, is this.
b1 = 101711 # basis between N1... and N2...
b2 = 10111 # basis between N10.... and N11....



def suffix(rem):
    """ Produces the alpha(numeric) suffix from a number 0 - 950 """
    if rem == 0:
        suf = ''
    else:
        if rem <= 600: #Class A suffix -- only letters.
            rem = rem - 1
            suf = base34[rem // 25]
            if rem % 25 > 0:
                suf = suf + base34[rem % 25 - 1]# second class A letter, if present.
        else:  #rems > 600 : First digit of suffix is a number.  Second digit may be blank, letter, or number.
            rem = rem - 601
            suf = base10[rem // 35]
            if rem % 35 > 0:
                suf = suf + base34[rem % 35 - 1]
    return suf

def enc_suffix(suf):
    """ Produces a remainder from a 0 - 2 digit suffix.
    No error checking.  Using illegal strings will have strange results."""
    if len(suf) == 0:
        return 0
    r0 = base34.find(suf[0])
    if len(suf) == 1:
        r1 = 0
    else:
        r1 = base34.find(suf[1]) + 1
    if r0 < 24: # first char is a letter, use base 25
        return r0 * 25 + r1 + 1
    else:  # first is a number -- base 35.
        return r0 * 35 + r1 - 239

def icao_to_tail(icao):
    if (icao < 0) or (icao > 0xadf7c7):
        return "Undefined"
    icao = icao - icaooffset
    d1 = icao // b1
    nnum = 'N' + base9[d1]
    r1 = icao % b1
    if r1 < 601:
        nnum = nnum + suffix(r1) # of the form N1ZZ
    else:
        d2 = (r1 - 601) // b2  # find second digit.
        nnum = nnum + base10[d2]
        r2 = (r1 - 601) % b2  # and residue after that
        if r2 < 601:  # No third digit. (form N12ZZ)
            nnum = nnum + suffix(r2)
        else:
            d3 = (r2 - 601) // 951 # Three-digits have extended suffix.
            r3 = (r2 - 601) % 951
            nnum = nnum + base10[d3] + suffix(r3)
    return nnum

def tail_to_icao(tail):
    if tail[0] != 'N':
        return -1
    icao = icaooffset
    icao = icao + base9.find(tail[1]) * b1
    if len(tail) == 2: # simple 'N3' etc.
        return icao
    d2 = base10.find(tail[2])
    if d2 == -1: # Form N1A
        icao = icao + enc_suffix(tail[2:4])
        return icao
    else: # Form N11... or N111..
        icao = icao + d2 * b2 + 601
        d3 = base10.find(tail[3])
        if d3 > -1: #Form N111 Suffix is base 35.
            icao = icao + d3 * 951 + 601
            icao = icao + enc_suffix(tail[4:6])
            return icao
        else:  #Form N11A
            icao = icao + enc_suffix(tail[3:5])
            return icao
