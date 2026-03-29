import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../utils/api';

export const useTransactions = () => {
  return useQuery({
    queryKey: ['transactions'],
    queryFn: async () => {
      // Mocked endpoint behavior, replace with api.get('/transactions') later
      return [
        { id: 1, date: 'Mar 12, 2026', desc: 'Office Supplies', category: 'Office', amount: -45.99 },
        { id: 2, date: 'Mar 11, 2026', desc: 'Client Lunch', category: 'Food', amount: -67.50 },
      ];
    },
  });
};

export const useCreateTransaction = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (newTx) => {
      // Replace with actual API call
      return newTx;
    },
    onSuccess: () => {
       queryClient.invalidateQueries({ queryKey: ['transactions'] });
    },
  });
};
