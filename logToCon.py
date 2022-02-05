import logging

# init logging
log = logging.getLogger()
log.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
form = logging.Formatter('%(message)s')
console.setFormatter(form)
log.addHandler(console)
