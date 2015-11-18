# Currently working on GUI for DBC. Python code follows

#!/usr/bin/env python
# coding:utf-8

""" DetailsPanel.py

    The DetailsPanel accepts the following information:

        # PricePanel.py #
        mileage (read-only)
        base price (read-only)
        price modifier (read-only)
        calculated price (read-only)
        has price override
        price override
        actual price (read-only)

        # DateTimePanel.py #
        timeEntered
        timeAcknowledged
        timePickedUp
        calculatedDeliveryTime
        hasDeliveryTimeOverride
        deliveryTimeOverride
        actualDeliveryTime
        lateJobExempt
        recipientsName

        # OptionsPanel.py #

    This panel listens for changes to the following fields:

        pickupStreetAddress  -- ignored for now.
        pickupZone           -- ignored for now.
        pickupZipCode
        dropoffStreetAddress -- ignored for now.
        dropoffZone          -- ignored for now.
        dropoffZipCode

    It notifies the editor when the following fields are changed:

        mileage

"""
_author_ = "Bill Golembieski 9/29/2015"
_email_ = "BillGolembieski@projectu23.com"
_status_ = "Prototype" #Development -> Prototype -> Production

import string
import wx

# import calendar

##### DateTime #####
InputPanel         = Framework.get("shared.Editor").InputPanel
Editor             = Framework.get("shared.Editor")
BooleanInputField  = Framework.get("shared.Editor").BooleanInputField
DateTimeInputField = Framework.get("shared.Editor").DateTimeInputField
DateSelector       = Framework.get("shared.Editor").DateSelector
DatePickerCtrl     = Framework.get("shared.Editor").DatePickerCtrl
PopupInputField    = Framework.get("shared.Editor").PopupInputField
Database           = Framework.get("shared.Database")
Calculator         = Framework.get("shared.Calculator")

##### Price #####
MoneyInputField    = Framework.get("shared.Editor").MoneyInputField
FloatInputField    = Framework.get("shared.Editor").FloatInputField
DisplayField       = Framework.get("shared.Editor").DisplayField

##### Options #####
TextInputField     = Framework.get("shared.Editor").TextInputField

#############################################################################

class SubPanel(InputPanel):
    """Create a SubPanel
    """
    def __init__(self, parent, editor, showRoundTripField=False):
        """
        :param parent:
        :param editor:
        :param showRoundTripField:
        :return:
        """
        InputPanel.__init__(self, parent)
        self._editor = editor

        self.layout()

    def recordToPanel(self, rec):
        """ Override InputPanel.recordToPanel().

            If we are not showing the "round trip" field, we keep track of this
            value internally.
        """
        InputPanel.recordToPanel(self, rec)
        if not self._showRoundTripField:
            self._roundTrip = rec.get("roundTrip", False)


    def panelToRecord(self, rec):
        """ Override InputPanel.panelToRecord().

            If we are not showing the "round trip" field, we keep track of this
            value internally.
        """
        InputPanel.panelToRecord(self, rec)
        if not self._showRoundTripField:
            rec['roundTrip'] = self._roundTrip


    def setFieldValue(self, field, value):
        """ Override InputPanel.setFieldValue().

            If we are not showing the "round trip" field, we keep track of this
            value internally.
        """
        if not self._showRoundTripField and field == "roundTrip":
            self._roundTrip = value
        else:
            InputPanel.setFieldValue(self, field, value)

    # =====================
    # == PRIVATE METHODS ==
    # =====================

    def _onCustomerChanged(self, customer):
        """ Respond to the customer value changing.
        """
        if customer in [-1, None]:
            results = []
        else:
            results = Database.select("Customer", ["jobRequiresPODWithEmailBack",
                                                   "jobRequiresPOD",
                                                   "jobRequiresPODWithCallBack"],
                                      "id="+str(customer))

        if len(results) == 1:
            cust = results[0]
        else:
            cust = {}

        if cust.get("jobRequiresPODWithEmailBack") == "true":
            jobRequiresPODWithEmailBack = True
        else:
            jobRequiresPODWithEmailBack = False
        if cust.get("jobRequiresPOD") == "true":
            jobRequiresPOD = True
        else:
            jobRequiresPOD = False
        if cust.get("jobRequiresPODWithCallBack") == "true":
            jobRequiresPODWithCallBack = True
        else:
            jobRequiresPODWithCallBack = False

        self._requiresPODWithEmailBackField.setValue(jobRequiresPODWithEmailBack)
        self._requiresPODField.setValue(jobRequiresPOD)
        self._requiresPODWithCallBackField.setValue(jobRequiresPODWithCallBack)


class DetailsPanel(InputPanel):
    """ The "Details" input panel.
    """
    def __init__(self, parent, editor, showRoundTripField=False):
        """
        :param parent: Standard initializer
        :param editor: the InputEditor this panel belongs to. If
        'showRoundTripField' is set to False, the "round trip" checkbox is
        shown; this allows us to hide this field if not wanted.
        """

        InputPanel.__init__(self, parent)

        self._editor = editor
        self._showRoundTripField = showRoundTripField
        self._origPickupZipCode  = None
        self._origDropoffZipCode = None

        self._pricePan = SubPanel(self, parent)
        self._timePan  = SubPanel(self, parent)

        # Add panels next to each other in the same row
        self.startRow()
        self.addField(None, self._timePan,  None)
        self.addField(None, self._pricePan, None)
        self.endRow()

        ##################### Define input fields for _timePan #####################
        #
        #  Note: this ordering is REQUIRED to TAB properly from one field to the next
        #
        self._timePan._recipientsNameField           = TextInputField(self._timePan,
                                                                      displayWidth=15, editWidth=32)
        self._timePan._prebookedField                = BooleanInputField(self._timePan,
                                                                         "Prebooked Job")
        self._timePan._readyAtField                  = DateTimeInputField(self._timePan)
        self._timePan._deliverByField                = DateTimeInputField(self._timePan)
        self._timePan._timeEnteredField              = DateTimeInputField(self._timePan)
        self._timePan._timeAcknowledgedField         = DateTimeInputField(self._timePan)
        self._timePan._timePickedUpField             = DateTimeInputField(self._timePan)
        self._timePan._calcDeliveryTimeField         = DateTimeInputField(self._timePan)
        self._timePan._calcDeliveryTimeField.setReadOnly()
        self._timePan._hasDeliveryTimeOverrideField  = BooleanInputField(self._timePan,
                                                                         "Has Delivery Time Override")
        self._timePan._deliveryTimeOverrideField     = DateTimeInputField(self._timePan)
        self._timePan._actualDeliveryTimeField       = DateTimeInputField(self._timePan)
        self._timePan._actualDeliveryTimeField.setReadOnly()
        self._timePan._lateJobExemptField            = BooleanInputField(self._timePan,
                                                                         "Late Job Exempt")
        self._timePan._okayToLeaveField              = BooleanInputField(self._timePan,
                                                                         "OK To Leave")
        self._timePan._requiresPODField              = BooleanInputField(self._timePan,
                                                                         "Requires POD")
        self._timePan._requiresPODWithCallBackField  = BooleanInputField(self._timePan,
                                                                         "Requires POD with Call Back")
        self._timePan._requiresPODWithEmailBackField = BooleanInputField(self._timePan,
                                                                         "Requires POD with Email Back")
        if showRoundTripField:
            self._timePan._roundTripField            = BooleanInputField(self._timePan,
                                                                         "Round Trip Job")
        else:
            # Keep track of this value internally.
            self._timePan._roundTrip = False

        # self._suppressDataMessageField = BooleanInputField(self._timePan,
        #                                                    "Suppress Data Message")
        # self._timePan._dateForBillingField           = DateTimeInputField(self._timepan,
        #                                                                   useTime=False)

        ##################### Define input fields for _pricePan #####################
        #
        #  Note: this ordering is REQUIRED to Tab properly from one field to the next
        #
        self._pricePan._mileageField              = FloatInputField(self._pricePan, editWidth=12,
                                                                    displayWidth=12)
        self._pricePan._mileageField.setReadOnly()
        self._pricePan._basePriceField            = MoneyInputField(self._pricePan, editWidth=12,
                                                                    displayWidth=12)
        self._pricePan._basePriceField.setReadOnly()
        self._pricePan._priceModifierField        = MoneyInputField(self._pricePan, editWidth=12,
                                                                    displayWidth=12)
        self._pricePan._priceModifierField.setReadOnly()
        self._pricePan._calculatedPriceField      = MoneyInputField(self._pricePan, editWidth=12,
                                                                    displayWidth=12)
        self._pricePan._calculatedPriceField.setReadOnly()
        self._pricePan._defaultStandardPriceField = MoneyInputField(self._pricePan, editWidth=12,
                                                                    displayWidth=12)
        self._pricePan._defaultStandardPriceField.setReadOnly()
        self._pricePan._hasPriceOverrideField     = BooleanInputField(self._pricePan,
                                                                  "Has Price Override")
        self._pricePan._priceOverrideField        = MoneyInputField(self._pricePan, editWidth=12,
                                                                    displayWidth=12)
        self._pricePan._actualPriceField          = MoneyInputField(self._pricePan, editWidth=12,
                                                                    displayWidth=12)
        self._pricePan._actualPriceField.setReadOnly()

        ##################### Layout _timePan contents #####################
        self._timePan.addField("Recipient's Name",         self._timePan._recipientsNameField,
                               "recipientsName")
        # ------------------------------
        self._timePan.addVerticalGap(5)
        # ------------------------------
        self._timePan.addField(None,                       self._timePan._prebookedField,
                               "isPrebooked")
        # self._timePan.addField("Ready At",                self._readyAtField,
        #                      "timeEntered")
        self._timePan.addField("Ready At",                 self._timePan._readyAtField,
                               "readyAt")
        self._timePan.addField("Deliver By",               self._timePan._deliverByField,
                               "deliverBy")
        # ------------------------------
        self._timePan.addVerticalGap(5)
        # ------------------------------
        self._timePan.addField("Time Entered",             self._timePan._timeEnteredField,
                               "timeEntered")
        self._timePan.addField("Time Acknowledged",        self._timePan._timeAcknowledgedField,
                               "timeAcknowledged")
        self._timePan.addField("Time Picked Up",           self._timePan._timePickedUpField,
                               "timePickedUp")
        # ------------------------------
        self._timePan.addVerticalGap(5)
        # ------------------------------
        self._timePan.addField("Calculated Delivery Time", self._timePan._calcDeliveryTimeField,
                               "calculatedDeliveryTime")
        self._timePan.addField(None,                       self._timePan._hasDeliveryTimeOverrideField,
                               "hasDeliveryTimeOverride")
        self._timePan.addField("Delivery Time Override",   self._timePan._deliveryTimeOverrideField,
                               "deliveryTimeOverride")
        self._timePan.addField("Actual Delivery Time",     self._timePan._actualDeliveryTimeField,
                               "actualDeliveryTime")
        self._timePan.addField(None, self._timePan._lateJobExemptField, "lateJobExempt")

        # ------------------------------
        self._timePan.addVerticalGap(5)
        # ------------------------------
        self._timePan.addField(None,                       self._timePan._okayToLeaveField,
                               "okayToLeave")
        self._timePan.addField(None,                       self._timePan._requiresPODField,
                               "requiresPOD")
        self._timePan.addField(None,                       self._timePan._requiresPODWithCallBackField,
                               "requiresPODWithCallBack")
        self._timePan.addField(None,                       self._timePan._requiresPODWithEmailBackField,
                               "requiresPODWithEmailBack")

        if showRoundTripField:
            self._timePan.addField(None, self._timePan._roundTripField, "roundTrip")

        # self._timePan.addField(None, self._suppressDataMessageField,
        #              "suppressDataMessage")

        self._timePan.layout()

        ##################### Layout _pricePan contents #####################
        self._pricePan.addField("Mileage",                  self._pricePan._mileageField,
                                "mileage")
        # ------------------------------
        self._pricePan.addVerticalGap(10)
        # ------------------------------
        self._pricePan.addField("Price",                    self._pricePan._basePriceField,
                                "basePrice")
        self._pricePan.addField("Price Modifier",           self._pricePan._priceModifierField,
                                "priceModifier")
        self._pricePan.addField("Calculated Price",         self._pricePan._calculatedPriceField,
                                "calculatedPrice")
        self._pricePan.addField("DBC Standard Price ",      self._pricePan._defaultStandardPriceField,
                                "defaultStandardBasePrice")
        # ------------------------------
        self._pricePan.addVerticalGap(5)
        # ------------------------------
        self._pricePan.addField(None,                       self._pricePan._hasPriceOverrideField,
                                "hasPriceOverride")
        self._pricePan.addField("Price Override",           self._pricePan._priceOverrideField,
                                "priceOverride")
        # ------------------------------
        self._pricePan.addVerticalGap(10)
        # ------------------------------
        self._pricePan.addField("Actual Price To Customer", self._pricePan._actualPriceField,
                                "actualPrice")
        self._pricePan.layout()


        # Prepare to catch the field value changes we want to respond to at the
        # input panel level.

        editor.registerFieldListener("pickupZipCode", self._onPickupZipChanged)
        editor.registerFieldListener("dropoffZipCode",
                                                     self._onDropoffZipChanged)
        editor.registerFieldListener("customer", self._onCustomerChanged)

        self.layout()

        # TODO: add support for recalculating actual times as values are
        # entered.




    def recordToPanel(self, rec):
        """ Override InputPanel.recordToPanel().

            If we are not showing the "round trip" field, we keep track of this
            value internally.
        """
        ##Price Panel##
        self._origPickupZipCode  = rec.get("pickupZipCode")
        self._origDropoffZipCode = rec.get("dropoffZipCode")

        ## Options Panel ##
        InputPanel.recordToPanel(self, rec)
        if not self._showRoundTripField:
            self._timePan._roundTrip = rec.get("roundTrip", False)


    def panelToRecord(self, rec):
        """ Override InputPanel.panelToRecord().

            If we are not showing the "round trip" field, we keep track of this
            value internally.
        """
        ##Price Panel##
        self._origPickupZipCode  = rec.get("pickupZipCode")
        self._origDropoffZipCode = rec.get("dropoffZipCode")

        InputPanel.panelToRecord(self._pricePan, rec)
        InputPanel.panelToRecord(self._timePan, rec) #EHH?

        if not self._showRoundTripField:
            rec['roundTrip'] = self._timePan._roundTrip


    def setFieldValue(self, field, value):
        """ Override InputPanel.setFieldValue().

            If we are not showing the "round trip" field, we keep track of this
            value internally.
        """
        if not self._showRoundTripField and field == "roundTrip":
            self._timePan._roundTrip = value
        else:
            InputPanel.setFieldValue(self, field, value)

    def _onPickupZipChanged(self, pickupZipCode):
        """ Respond to the user changing the pickup zip code.

            We recalculate the mileage based on our new information.
        """
        dropoffZipCode = self._editor.getFieldValue("dropoffZipCode")
        if dropoffZipCode in [-1, None]:
            # The dropoff zip code hasn't changed -> use original value.
            dropoffZipCode = self._origDropoffZipCode

        self._calcMileage(pickupZipCode, dropoffZipCode)

    def _onDropoffZipChanged(self, dropoffZipCode):
        """ Respond to the user changing the dropoff zip code.

            We recalculate the mileage based on our new information.
        """
        pickupZipCode = self._editor.getFieldValue("pickupZipCode")
        if pickupZipCode in [-1, None]:
            # The pickup zip code hasn't changed -> use original value.
            pickupZipCode = self._origPickupZipCode

        self._calcMileage(pickupZipCode, dropoffZipCode)

    # =====================
    # == PRIVATE METHODS ==
    # =====================

    def _onCustomerChanged(self, customer):
        """ Respond to the customer value changing.
        """
        if customer in [-1, None]:
            results = []
        else:
            results = Database.select("Customer", ["jobRequiresPODWithEmailBack",
                                                   "jobRequiresPOD",
                                                   "jobRequiresPODWithCallBack"],
                                      "id="+str(customer))

        if len(results) == 1:
            cust = results[0]
        else:
            cust = {}

        if cust.get("jobRequiresPODWithEmailBack") == "true":
            jobRequiresPODWithEmailBack = True
        else:
            jobRequiresPODWithEmailBack = False
        if cust.get("jobRequiresPOD") == "true":
            jobRequiresPOD = True
        else:
            jobRequiresPOD = False
        if cust.get("jobRequiresPODWithCallBack") == "true":
            jobRequiresPODWithCallBack = True
        else:
            jobRequiresPODWithCallBack = False

        self._timePan._requiresPODWithEmailBackField.setValue(jobRequiresPODWithEmailBack)
        self._timePan._requiresPODField.setValue(jobRequiresPOD)
        self._timePan._requiresPODWithCallBackField.setValue(jobRequiresPODWithCallBack)

    def _calcMileage(self, pickupZipCode, dropoffZipCode):
        """ Recalculate the mileage for this job.
        """
        if pickupZipCode != None and dropoffZipCode != None:
            mileage = Calculator.calculateMileage(None, None, pickupZipCode,
                                                  None, None, dropoffZipCode)
        else:
            mileage = None

        self._pricePan._mileageField.setValue(mileage)
        self._editor.fieldChanged("mileage", mileage)
