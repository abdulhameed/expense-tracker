import React, { useState } from 'react';
import { Modal } from '../../components/ui/Modal';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';

export const CreateTransactionModal = ({ isOpen, onClose }) => {
  const [type, setType] = useState('expense');

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Create Transaction"
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button variant="primary">Save</Button>
        </>
      }
    >
      <div className="space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium text-neutral-700 block">Transaction Type</label>
          <div className="flex gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input 
                type="radio" 
                name="type" 
                value="expense"
                checked={type === 'expense'}
                onChange={(e) => setType(e.target.value)}
                className="w-4 h-4 text-primary-600 focus:ring-primary-500"
              />
              <span className="text-neutral-700">Expense</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input 
                type="radio" 
                name="type" 
                value="income"
                checked={type === 'income'}
                onChange={(e) => setType(e.target.value)}
                className="w-4 h-4 text-primary-600 focus:ring-primary-500"
              />
              <span className="text-neutral-700">Income</span>
            </label>
          </div>
        </div>
        
        <Input label="Title" placeholder="Enter transaction title" />
        
        <Input 
          label="Amount" 
          type="number" 
          step="0.01" 
          placeholder="0.00" 
          leftIcon="$" 
          className="font-mono text-lg" 
        />
        
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-neutral-700 block">Category</label>
            <select className="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 text-neutral-900 bg-white">
              <option>Select a category</option>
              <option>Food & Dining</option>
              <option>Transportation</option>
              <option>Shopping</option>
            </select>
          </div>
          <Input label="Date" type="date" />
        </div>
        
        <Input label="Description (Optional)" placeholder="Brief context" />
      </div>
    </Modal>
  );
};
