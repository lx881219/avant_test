class Line:
    def __init__(self, credit, apr, date):
        """
        For the Line class I use a list of dictionary to store all billing cycles, If we need to store data to database,
        then we should use a cycle class.
        """
        self.credit = credit
        self.apr = apr
        self.cycles = [{
            'begin_balance': 0,
            'begin_out_balance': 0,
            # Here we use another list of dictionary to store all transactions within this billing cycle
            'transactions': [],
            'balance': 0,
            'out_balance': 0,
            'closed': False
        }]

    def draw(self, amount, date):
        """
        Draw money
        :param amount: amount drew
        :param date:  transaction date
        :return:
        """
        credit = self.credit - self.get_balance(date)
        if amount > credit:
            print "Transaction Declined! You do not have enough credit!"
        else:
            self.record_transactions(amount, date)

        return

    def pay(self, amount, date):
        """
        Make Payment
        :param amount: amount paid
        :param date:  transaction date
        :return:
        """
        balance = self.get_balance(date)
        if amount > balance:
            print "Transaction Declined! Your Payment exceed the current balance!"
        else:
            self.record_transactions(-amount, date)

        return

    def record_transactions(self, amount, date):
        """
        Record each transactions
        :param amount: amount in this transaction, if positive, drew, if negative, paid
        :param date: transaction date
        :return:
        """
        # Get index of corresponding cycle, Make sure the current transaction falls into correct cycle.
        index_of_cycle = self.find_cycle(date)

        # get last_out_balance if there are already at least one transaction in current cycle
        if self.cycles[index_of_cycle]['transactions']:
            last_out_balance = self.cycles[index_of_cycle]['transactions'][-1]['out_balance']
        # No Transaction in current cycle
        else:
            last_out_balance = self.cycles[index_of_cycle]['begin_out_balance']

        # Update new outstanding balance
        curr_out_balance = last_out_balance + amount

        # Create a new transaction dictionary
        new_transacion = {
            'date': date,
            'amount': amount,
            'out_balance': curr_out_balance
        }

        # Add new transaction to current cycle
        self.cycles[index_of_cycle]['transactions'].append(new_transacion)

        return

    def check(self, date):
        """
        Check balance and interest
        :param date: date need to check
        :return:
        """

        # Get index of corresponding cycle based on date
        index_of_cycle = self.find_cycle(date)

        # get current outstanding balance
        # There is at least one transaction in current cycle
        if self.cycles[index_of_cycle]['transactions']:
            for index_of_transaction in range(len(self.cycles[index_of_cycle]['transactions'])-1, -1, -1):
                if self.cycles[index_of_cycle]['transactions'][index_of_transaction]['date'] <= date:
                    curr_out_balance = self.cycles[index_of_cycle]['transactions'][index_of_transaction]['out_balance']
                    break
        # No transactions yet
        else:
            curr_out_balance = self.cycles[index_of_cycle]['begin_balance']

        # if (within 30 days and no begin balance) or (all balance paid off)
        if self.cycles[index_of_cycle]['begin_balance'] == 0 or curr_out_balance == 0:
            print "Balance: %f Interest: 0 on day %s" % (curr_out_balance, date)

        else:
            # Get latest out balance
            if self.cycles[index_of_cycle]['transactions']:
                last_out_balance = self.cycles[index_of_cycle]['transactions'][-1]['out_balance']
            else:
                last_out_balance = self.cycles[index_of_cycle]['begin_out_balance']

            # Get current balance
            curr_balance = self.get_balance(date)
            curr_interest = curr_balance - last_out_balance

            print "Balance: %f Interest: %f on day %s" % (curr_balance, curr_interest, date)

        return

    def show_statement(self):
        """
        Show details for each billing cycle
        :return:
        """
        print "Statement:"
        for index_of_cycle in range(len(self.cycles)):

            print "Cycle: %d" % (index_of_cycle+1)

            # print each transaction in current cycle
            print('Transactions: {')
            for record in self.cycles[index_of_cycle]['transactions']:
                if record['amount'] < 0:
                    print "$%f is paid on day %s" % (-record['amount'], record['date'])
                else:
                    print "$%f is drew on day %s" % (record['amount'], record['date'])
            print '}'

            # Print cycle summary
            print "Balance when cycle begins: %f" % self.cycles[index_of_cycle]['begin_balance']
            print "Outstanding balance when cycle begin: %f" % self.cycles[index_of_cycle]['begin_out_balance']
            if self.cycles[index_of_cycle]['closed']:
                print "Cycle closed: %s" % "Yes"
                print "Balance when cycle ends: %f" % self.cycles[index_of_cycle]['balance']
                print "Outstanding balance when cycle ends: %f" % self.cycles[index_of_cycle]['out_balance']
                print "Remain credit: %f" % (self.credit - self.cycles[index_of_cycle]['balance'])
            else:
                print "Cycle closed: %s" % "No"

        return

    def find_cycle(self, date):
        """
        Check which cycle the given date falls into, if cycle doesn't exist, create it
        :param date: given date
        :return: index of the correct cycle
        """
        index_of_cycle = date / 30
        # Create cycle if needed
        while index_of_cycle >= len(self.cycles):
            last_cycle = self.cycles[-1]

            #close last cycle
            if not self.cycles[-1]['closed']:
                self.close_cycle(len(self.cycles)-1)

            # Create a new cycle
            last_balance = last_cycle['balance']
            last_out_balance = last_cycle['out_balance']
            self.cycles.append({
                'begin_balance': last_balance,
                'begin_out_balance': last_out_balance,
                'transactions': [],
                'balance': last_balance,
                'out_balance': last_out_balance,
                'closed': False,
            })

        return index_of_cycle

    def close_cycle(self, index):
        """
        Close the given billing cycle, calculate ending balance and out standing balance
        :param index: index of the cycle
        :return:
        """
        interest = 0
        # check if there is at least one transaction in current cycle
        if self.cycles[index]['transactions']:
            last_day = 0
            last_out_balance = self.cycles[index]['begin_out_balance']
            last_balance = self.cycles[index]['begin_balance']
            # Update interest, outstanding balance and balance after each transaction
            for transaction in self.cycles[index]['transactions']:
                date_in_cycle = transaction['date'] % 30
                interest += last_out_balance * self.apr / 365 * (date_in_cycle - last_day)
                last_day = date_in_cycle
                last_out_balance += transaction['amount']
                last_balance += transaction['amount']
            # Update interest, outstanding balance and balance after last transaction
            interest += last_out_balance * self.apr / 365 * (30 - last_day)
            self.cycles[index]['out_balance'] = last_out_balance
            self.cycles[index]['balance'] = last_balance + interest

        # No transaction
        else:
            interest += self.cycles[index]['begin_out_balance'] * self.apr / 365 * 30
            self.cycles[index]['balance'] += interest

        self.cycles[index]['closed'] = True

        return

    def get_balance(self, date):
        """
        Get balance based on given date
        :param date:
        :return:
        """
        # Get index of corresponding cycle based on date
        index = self.find_cycle(date)

        balance = self.cycles[index]['begin_balance']
        interest = 0

        last_day = 0
        given_date_in_cycle = date % 30

        # update interest, outstanding balance and balance after each transaction before given date
        if self.cycles[index]['transactions']:
            last_out_balance = self.cycles[index]['begin_out_balance']
            for transaction in self.cycles[index]['transactions']:
                if transaction['date'] <= date:
                    transaction_date_in_cycle = transaction['date'] % 30
                    interest += last_out_balance * self.apr / 365 * (transaction_date_in_cycle - last_day)
                    last_day = transaction_date_in_cycle
                    last_out_balance += transaction['amount']
                    balance += transaction['amount']

        # update interest, outstanding balance and balance after last transaction and before given date
        interest += self.cycles[index]['begin_out_balance'] * self.apr / 365 * (given_date_in_cycle-last_day)
        balance += interest

        return balance

if __name__ == "__main__":
    """
    Here is 2 given scenarios and one customized test case.
    I didn't create a interface for this program, sorry for the inconvenient. But you can use the method to create
    your own test case. Note that the date in all method should be in a increasing order
    Methods:
    Line.check(date)
        check the current balance and interest
    Line.draw(amount, date)
        draw money
    Line.pay(amount, date)
        Pay balance
    Line.show_statement()
        Show details of all billing cycles
    """

    # Scenario 1
    print 'Scenario 1:'
    scenario1 = Line(1000, 0.35, 0)
    scenario1.check(0)
    scenario1.draw(500, 0)
    scenario1.check(29)
    scenario1.check(30)
    scenario1.show_statement()

    # Scenario 2
    print 'Scenario 2:'
    scenario2 = Line(1000, 0.35, 0)
    scenario2.check(0)
    scenario2.draw(500, 0)
    scenario2.pay(200, 15)
    scenario2.draw(100, 25)
    scenario2.check(29)
    scenario2.check(30)
    scenario2.show_statement()

    # Customized Line
    print 'Customized Line:'
    line1 = Line(1000, 0.35, 0)
    line1.check(0)
    line1.draw(500, 0)
    line1.draw(600, 5)
    line1.pay(200, 15)
    line1.draw(100, 25)
    line1.check(29)
    line1.check(30)
    line1.pay(200, 45)
    line1.pay(500, 50)
    line1.check(45)
    line1.check(60)
    line1.show_statement()
