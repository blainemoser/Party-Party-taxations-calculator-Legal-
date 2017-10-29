class Taxations:
  def __init__(self, feesGross, feesTO, disbGross, disbTO):

    self.feesGross = feesGross
    self.feesTO = feesTO
    self.disbGross = disbGross
    self.disbTO = disbTO

## rewrite the totals:
## calc proper
class HighCourtTaxations(Taxations):
  def __init__(self, *args, **kwargs):
	  super(HighCourtTaxations, self).__init__(*args, **kwargs)
	  self.feesTot =              self.feesGross - self.feesTO
	  self.disbTot =              self.disbGross - self.disbTO
	  self.draw_fee =             self.feesTot*0.106
	  self.attendance_levy =      self.feesTot+self.draw_fee+self.disbTot
	  self.subTot1 =              self.feesTot + self.draw_fee
	  self.addDisb =              self.disbTot
	  self.subTot2 =              self.subTot1 + self.addDisb
	  if self.attendance_levy <= 10000:
		  self.attendance_fee =  self.attendance_levy*0.106
	  elif self.attendance_levy <= 20000:
		  self.attendance_fee =  1060 + ((self.attendance_levy-10000)*0.0510)
	  else:
		  self.attendance_fee =  1570 + ((self.attendance_levy-20000)*0.0212)
	  self.vat =                  0.14*((self.attendance_levy+self.attendance_fee) 
                                   - self.disbTot)
	  self.grandTot =             self.subTot2 + self.attendance_fee + self.vat


class MagCourtTaxations(Taxations):
  def __init__(self, *args, **kwargs):
	  super(MagCourtTaxations, self).__init__(*args, **kwargs)
	  self.feesTot =         self.feesGross - self.feesTO
	  self.disbTot =         self.disbGross - self.disbTO
	  self.draw_fee =        self.feesTot*0.05
	  self.attendance_levy = self.feesTot+self.draw_fee+self.disbTot
	  self.subTot1 =         self.feesTot + self.draw_fee
	  self.addDisb =         self.disbTot
	  self.subTot2 =         self.subTot1 + self.addDisb
	  self.attendance_fee =  self.attendance_levy*0.05
	  self.vat = 0.14*((self.attendance_levy+self.attendance_fee) - self.disbTot)
	  self.grandTot =        self.subTot2 + self.attendance_fee + self.vat
