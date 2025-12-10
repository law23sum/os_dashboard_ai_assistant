import { useQuery } from '@tanstack/react-query'
import { fetchSettings } from '../api/settings'

export const useAppSettings = () => {
  return useQuery({
    queryKey: ['settings'],
    queryFn: fetchSettings,
  })
}
